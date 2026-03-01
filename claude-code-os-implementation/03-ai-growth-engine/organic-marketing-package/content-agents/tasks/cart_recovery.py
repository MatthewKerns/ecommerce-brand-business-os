"""
Cart Recovery Celery Tasks

This module contains Celery tasks for automated abandoned cart recovery,
including email sequence scheduling and sending.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from celery import Task
from celery_app import app
from database.connection import get_db_session
from database.models import AbandonedCart, CartItem, CartRecoveryEmail
from services.cart_service import CartService
from services.email_service import EmailService, EmailServiceError
from logging_config import get_logger

logger = get_logger("cart_recovery_tasks")


class CartRecoveryTask(Task):
    """
    Base task class for cart recovery tasks with database session management
    """
    _cart_service = None
    _email_service = None

    @property
    def cart_service(self):
        """Lazy initialization of CartService"""
        if self._cart_service is None:
            self._cart_service = CartService()
        return self._cart_service

    @property
    def email_service(self):
        """Lazy initialization of EmailService"""
        if self._email_service is None:
            self._email_service = EmailService()
        return self._email_service


@app.task(
    bind=True,
    base=CartRecoveryTask,
    name="tasks.cart_recovery.process_abandoned_carts",
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def process_abandoned_carts(self) -> dict:
    """
    Process carts that should be marked as abandoned and schedule recovery emails.

    This task runs periodically (every 5 minutes via Celery Beat) to:
    1. Find active carts that are 30+ minutes old
    2. Mark them as abandoned
    3. Schedule the 3-email recovery sequence

    Returns:
        Dictionary with processing statistics:
        - carts_processed: Number of carts marked as abandoned
        - sequences_scheduled: Number of email sequences scheduled
        - errors: Number of errors encountered

    Raises:
        Retry: Automatically retries on failure up to max_retries
    """
    logger.info("Starting abandoned cart processing")

    stats = {
        "carts_processed": 0,
        "sequences_scheduled": 0,
        "errors": 0
    }

    try:
        # Get carts that should be marked as abandoned (30+ min old, < 72 hours)
        abandoned_carts = self.cart_service.get_abandoned_carts(
            min_age_minutes=30,
            max_age_hours=72,
            exclude_sent_emails=True  # Only carts without recovery emails
        )

        logger.info(f"Found {len(abandoned_carts)} carts to process")

        for cart in abandoned_carts:
            try:
                # Mark cart as abandoned
                self.cart_service.mark_abandoned(cart.cart_id)
                stats["carts_processed"] += 1

                # Schedule recovery email sequence
                schedule_recovery_sequence.delay(cart.cart_id)
                stats["sequences_scheduled"] += 1

                logger.info(
                    f"Processed cart {cart.cart_id}: "
                    f"email={cart.email}, value=${cart.total_value:.2f}"
                )

            except Exception as e:
                stats["errors"] += 1
                logger.error(
                    f"Error processing cart {cart.cart_id}: {str(e)}",
                    exc_info=True
                )
                # Continue processing other carts even if one fails

        logger.info(
            f"Abandoned cart processing complete: "
            f"processed={stats['carts_processed']}, "
            f"scheduled={stats['sequences_scheduled']}, "
            f"errors={stats['errors']}"
        )

        return stats

    except Exception as e:
        logger.error(f"Fatal error in process_abandoned_carts: {str(e)}", exc_info=True)
        # Retry the entire task
        raise self.retry(exc=e)


@app.task(
    bind=True,
    base=CartRecoveryTask,
    name="tasks.cart_recovery.send_recovery_email",
    max_retries=3,
    default_retry_delay=600  # 10 minutes
)
def send_recovery_email(self, cart_id: str, email_type: str) -> dict:
    """
    Send a recovery email for an abandoned cart.

    Args:
        cart_id: Unique cart identifier
        email_type: Type of email to send (reminder, urgency, offer)

    Returns:
        Dictionary with email send result:
        - success: Whether email was sent successfully
        - cart_id: Cart identifier
        - email_type: Type of email sent
        - recipient: Email address
        - error: Error message if failed

    Raises:
        Retry: Automatically retries on failure up to max_retries
    """
    logger.info(f"Sending recovery email: cart_id={cart_id}, type={email_type}")

    result = {
        "success": False,
        "cart_id": cart_id,
        "email_type": email_type,
        "recipient": None,
        "error": None
    }

    db = get_db_session()

    try:
        # Get cart details
        cart = db.query(AbandonedCart).filter(AbandonedCart.cart_id == cart_id).first()

        if not cart:
            error_msg = f"Cart not found: {cart_id}"
            logger.error(error_msg)
            result["error"] = error_msg
            return result

        # Check if cart is still abandoned (not recovered or expired)
        if cart.status not in ["abandoned", "active"]:
            logger.info(
                f"Cart {cart_id} status is {cart.status}, skipping email"
            )
            result["error"] = f"Cart status is {cart.status}"
            return result

        result["recipient"] = cart.email

        # Get cart items
        cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

        # Prepare email context
        context = {
            "customer_name": cart.email.split("@")[0].capitalize(),  # Extract name from email
            "cart_items": [
                {
                    "name": item.product_name,
                    "price": float(item.price),
                    "quantity": item.quantity,
                    "image_url": item.product_image_url,
                    "subtotal": float(item.price) * item.quantity
                }
                for item in cart_items
            ],
            "total_value": float(cart.total_value),
            "currency": cart.currency,
            "recovery_link": cart.cart_url or f"{os.getenv('WEBSITE_URL', 'https://infinityvault.com')}/cart/recover/{cart.cart_id}",
            "platform": cart.platform,
            "discount_code": "SAVE10" if email_type == "offer" else None,
            "discount_amount": 10 if email_type == "offer" else None
        }

        # Map email_type to EmailService constants
        email_type_map = {
            "reminder": EmailService.EMAIL_TYPE_REMINDER,
            "urgency": EmailService.EMAIL_TYPE_URGENCY,
            "offer": EmailService.EMAIL_TYPE_OFFER
        }

        service_email_type = email_type_map.get(email_type)
        if not service_email_type:
            error_msg = f"Invalid email_type: {email_type}"
            logger.error(error_msg)
            result["error"] = error_msg
            return result

        # Determine sequence number
        sequence_map = {"reminder": 1, "urgency": 2, "offer": 3}
        sequence_number = sequence_map.get(email_type, 1)

        # Create or update email record
        email_record = db.query(CartRecoveryEmail).filter(
            CartRecoveryEmail.cart_id == cart.id,
            CartRecoveryEmail.email_type == email_type
        ).first()

        if not email_record:
            email_record = CartRecoveryEmail(
                cart_id=cart.id,
                sequence_number=sequence_number,
                email_type=email_type,
                status="pending"
            )
            db.add(email_record)

        # Send email
        try:
            self.email_service.send_cart_recovery_email(
                to_email=cart.email,
                email_type=service_email_type,
                context=context
            )

            # Update email record with success
            email_record.status = "sent"
            email_record.sent_at = datetime.utcnow()
            email_record.error_message = None

            result["success"] = True

            logger.info(
                f"Recovery email sent successfully: "
                f"cart_id={cart_id}, type={email_type}, to={cart.email}"
            )

        except EmailServiceError as e:
            # Update email record with error
            email_record.status = "failed"
            email_record.error_message = str(e)

            result["error"] = str(e)

            logger.error(
                f"Failed to send recovery email: "
                f"cart_id={cart_id}, type={email_type}, error={str(e)}"
            )

            # Retry on email send errors
            db.commit()
            raise self.retry(exc=e)

        # Commit database changes
        db.commit()

        return result

    except Exception as e:
        db.rollback()
        logger.error(
            f"Error in send_recovery_email: cart_id={cart_id}, error={str(e)}",
            exc_info=True
        )
        result["error"] = str(e)
        # Retry on unexpected errors
        raise self.retry(exc=e)

    finally:
        db.close()


@app.task(
    bind=True,
    base=CartRecoveryTask,
    name="tasks.cart_recovery.schedule_recovery_sequence",
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def schedule_recovery_sequence(self, cart_id: str) -> dict:
    """
    Schedule the complete 3-email recovery sequence for an abandoned cart.

    The sequence timing is:
    - Email 1 (reminder): Immediately (cart abandoned 30+ min ago)
    - Email 2 (urgency): 24 hours after abandonment
    - Email 3 (offer): 48 hours after abandonment

    Args:
        cart_id: Unique cart identifier

    Returns:
        Dictionary with scheduling result:
        - success: Whether scheduling was successful
        - cart_id: Cart identifier
        - emails_scheduled: List of scheduled email types
        - error: Error message if failed

    Raises:
        Retry: Automatically retries on failure up to max_retries
    """
    logger.info(f"Scheduling recovery sequence for cart: {cart_id}")

    result = {
        "success": False,
        "cart_id": cart_id,
        "emails_scheduled": [],
        "error": None
    }

    db = get_db_session()

    try:
        # Get cart details
        cart = db.query(AbandonedCart).filter(AbandonedCart.cart_id == cart_id).first()

        if not cart:
            error_msg = f"Cart not found: {cart_id}"
            logger.error(error_msg)
            result["error"] = error_msg
            return result

        # Check if cart is abandoned
        if cart.status != "abandoned":
            logger.warning(
                f"Cart {cart_id} is not abandoned (status={cart.status}), "
                f"skipping sequence scheduling"
            )
            result["error"] = f"Cart status is {cart.status}, not abandoned"
            return result

        # Use abandoned_at timestamp for scheduling, fall back to created_at
        reference_time = cart.abandoned_at or cart.created_at

        # Schedule Email 1 (reminder) - immediately
        send_recovery_email.apply_async(
            args=[cart_id, "reminder"],
            countdown=0  # Send immediately
        )
        result["emails_scheduled"].append("reminder")

        # Schedule Email 2 (urgency) - 24 hours after abandonment
        urgency_delay = timedelta(hours=24)
        urgency_eta = reference_time + urgency_delay
        send_recovery_email.apply_async(
            args=[cart_id, "urgency"],
            eta=urgency_eta
        )
        result["emails_scheduled"].append("urgency")

        # Schedule Email 3 (offer) - 48 hours after abandonment
        offer_delay = timedelta(hours=48)
        offer_eta = reference_time + offer_delay
        send_recovery_email.apply_async(
            args=[cart_id, "offer"],
            eta=offer_eta
        )
        result["emails_scheduled"].append("offer")

        result["success"] = True

        logger.info(
            f"Recovery sequence scheduled for cart {cart_id}: "
            f"reminder=now, urgency={urgency_eta.isoformat()}, offer={offer_eta.isoformat()}"
        )

        return result

    except Exception as e:
        logger.error(
            f"Error scheduling recovery sequence: cart_id={cart_id}, error={str(e)}",
            exc_info=True
        )
        result["error"] = str(e)
        # Retry on errors
        raise self.retry(exc=e)

    finally:
        db.close()
