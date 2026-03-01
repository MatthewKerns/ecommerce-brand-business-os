"""
Cart Service
Handles business logic for abandoned cart tracking, recovery, and analytics
"""
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database.connection import get_db_session
from database.models import AbandonedCart, CartItem, CartRecoveryEmail
from logging_config import get_logger


class CartService:
    """Service for managing abandoned cart tracking and recovery"""

    def __init__(self, db: Optional[Session] = None):
        """
        Initialize CartService

        Args:
            db: Optional SQLAlchemy session. If not provided, will create new sessions per operation.
        """
        self.logger = get_logger("cart_service")
        self._db = db

    def _get_session(self) -> Session:
        """
        Get database session.

        Returns:
            SQLAlchemy session
        """
        if self._db:
            return self._db
        return get_db_session()

    def _should_close_session(self) -> bool:
        """
        Determine if session should be closed after operation.

        Returns:
            True if we created the session, False if it was provided
        """
        return self._db is None

    def track_cart_event(
        self,
        cart_id: str,
        email: str,
        cart_items: List[Dict[str, Any]],
        platform: str = "website",
        user_id: Optional[str] = None,
        cart_url: Optional[str] = None
    ) -> AbandonedCart:
        """
        Track a cart event (creation or update).

        Args:
            cart_id: Unique cart identifier
            email: Customer email address
            cart_items: List of cart items with product_id, name, price, quantity
            platform: Source platform (website, tiktok_shop)
            user_id: Optional authenticated user ID
            cart_url: Optional cart recovery URL

        Returns:
            AbandonedCart instance

        Raises:
            ValueError: If cart_items is empty or invalid platform
        """
        self.logger.info(f"Tracking cart event: cart_id={cart_id}, email={email}, platform={platform}, items={len(cart_items)}")

        if not cart_items:
            raise ValueError("cart_items cannot be empty")

        if platform not in ["website", "tiktok_shop"]:
            raise ValueError(f"Invalid platform: {platform}. Must be 'website' or 'tiktok_shop'")

        db = self._get_session()
        try:
            # Calculate total value
            total_value = sum(
                float(item.get("price", 0)) * int(item.get("quantity", 1))
                for item in cart_items
            )

            # Check if cart exists
            cart = db.query(AbandonedCart).filter(AbandonedCart.cart_id == cart_id).first()

            if cart:
                # Update existing cart
                self.logger.debug(f"Updating existing cart: {cart_id}")
                cart.email = email
                cart.user_id = user_id
                cart.platform = platform
                cart.total_value = total_value
                cart.cart_url = cart_url
                cart.cart_data = json.dumps({"items": cart_items})
                cart.updated_at = datetime.utcnow()

                # Reset abandoned status if cart was previously abandoned
                if cart.status == "abandoned":
                    cart.status = "active"
                    cart.abandoned_at = None
                    self.logger.info(f"Cart {cart_id} reactivated after being abandoned")

                # Remove existing cart items and add new ones
                db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

            else:
                # Create new cart
                self.logger.debug(f"Creating new cart: {cart_id}")
                cart = AbandonedCart(
                    cart_id=cart_id,
                    user_id=user_id,
                    email=email,
                    platform=platform,
                    cart_data=json.dumps({"items": cart_items}),
                    cart_url=cart_url,
                    total_value=total_value,
                    currency="USD",
                    status="active"
                )
                db.add(cart)
                db.flush()  # Get the cart.id for cart items

            # Add cart items
            for item_data in cart_items:
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=item_data.get("product_id", ""),
                    product_name=item_data.get("name", ""),
                    product_image_url=item_data.get("image_url"),
                    quantity=int(item_data.get("quantity", 1)),
                    price=float(item_data.get("price", 0)),
                    currency="USD"
                )
                db.add(cart_item)

            db.commit()
            db.refresh(cart)

            self.logger.info(f"Successfully tracked cart: cart_id={cart_id}, total_value=${total_value:.2f}")
            return cart

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error tracking cart event: {str(e)}", exc_info=True)
            raise
        finally:
            if self._should_close_session():
                db.close()

    def mark_abandoned(self, cart_id: str) -> Optional[AbandonedCart]:
        """
        Mark a cart as abandoned.

        Args:
            cart_id: Cart identifier

        Returns:
            Updated AbandonedCart instance or None if not found
        """
        self.logger.info(f"Marking cart as abandoned: cart_id={cart_id}")

        db = self._get_session()
        try:
            cart = db.query(AbandonedCart).filter(AbandonedCart.cart_id == cart_id).first()

            if not cart:
                self.logger.warning(f"Cart not found: {cart_id}")
                return None

            if cart.status == "abandoned":
                self.logger.debug(f"Cart already marked as abandoned: {cart_id}")
                return cart

            cart.status = "abandoned"
            cart.abandoned_at = datetime.utcnow()
            cart.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(cart)

            self.logger.info(f"Successfully marked cart as abandoned: cart_id={cart_id}")
            return cart

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error marking cart as abandoned: {str(e)}", exc_info=True)
            raise
        finally:
            if self._should_close_session():
                db.close()

    def recover_cart(self, cart_id: str) -> Optional[AbandonedCart]:
        """
        Mark a cart as recovered (customer completed purchase).

        Args:
            cart_id: Cart identifier

        Returns:
            Updated AbandonedCart instance or None if not found
        """
        self.logger.info(f"Marking cart as recovered: cart_id={cart_id}")

        db = self._get_session()
        try:
            cart = db.query(AbandonedCart).filter(AbandonedCart.cart_id == cart_id).first()

            if not cart:
                self.logger.warning(f"Cart not found: {cart_id}")
                return None

            cart.status = "recovered"
            cart.recovered_at = datetime.utcnow()
            cart.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(cart)

            self.logger.info(f"Successfully marked cart as recovered: cart_id={cart_id}")
            return cart

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error marking cart as recovered: {str(e)}", exc_info=True)
            raise
        finally:
            if self._should_close_session():
                db.close()

    def get_abandoned_carts(
        self,
        min_age_minutes: int = 30,
        max_age_hours: int = 72,
        platform: Optional[str] = None,
        exclude_sent_emails: bool = False
    ) -> List[AbandonedCart]:
        """
        Get carts that should be marked as abandoned or need recovery emails.

        Args:
            min_age_minutes: Minimum age in minutes to consider abandoned (default: 30)
            max_age_hours: Maximum age in hours to still attempt recovery (default: 72)
            platform: Optional platform filter (website, tiktok_shop)
            exclude_sent_emails: If True, only return carts without recovery emails sent

        Returns:
            List of AbandonedCart instances
        """
        self.logger.info(
            f"Getting abandoned carts: min_age={min_age_minutes}min, "
            f"max_age={max_age_hours}h, platform={platform}"
        )

        db = self._get_session()
        try:
            now = datetime.utcnow()
            min_created_at = now - timedelta(minutes=min_age_minutes)
            max_created_at = now - timedelta(hours=max_age_hours)

            # Build query
            query = db.query(AbandonedCart).filter(
                and_(
                    AbandonedCart.status == "active",
                    AbandonedCart.created_at <= min_created_at,
                    AbandonedCart.created_at >= max_created_at
                )
            )

            # Filter by platform if specified
            if platform:
                query = query.filter(AbandonedCart.platform == platform)

            # Exclude carts with emails sent if requested
            if exclude_sent_emails:
                # Find cart IDs that have recovery emails
                sent_cart_ids = db.query(CartRecoveryEmail.cart_id).distinct().subquery()
                query = query.filter(~AbandonedCart.id.in_(sent_cart_ids))

            carts = query.all()

            self.logger.info(f"Found {len(carts)} abandoned carts matching criteria")
            return carts

        except Exception as e:
            self.logger.error(f"Error getting abandoned carts: {str(e)}", exc_info=True)
            raise
        finally:
            if self._should_close_session():
                db.close()

    def get_cart_by_id(self, cart_id: str) -> Optional[AbandonedCart]:
        """
        Get a cart by its cart_id.

        Args:
            cart_id: Cart identifier

        Returns:
            AbandonedCart instance or None if not found
        """
        self.logger.debug(f"Getting cart by ID: {cart_id}")

        db = self._get_session()
        try:
            cart = db.query(AbandonedCart).filter(AbandonedCart.cart_id == cart_id).first()

            if cart:
                self.logger.debug(f"Found cart: {cart_id}, status={cart.status}")
            else:
                self.logger.debug(f"Cart not found: {cart_id}")

            return cart

        except Exception as e:
            self.logger.error(f"Error getting cart by ID: {str(e)}", exc_info=True)
            raise
        finally:
            if self._should_close_session():
                db.close()

    def get_cart_items(self, cart_id: str) -> List[CartItem]:
        """
        Get all items for a cart.

        Args:
            cart_id: Cart identifier

        Returns:
            List of CartItem instances
        """
        self.logger.debug(f"Getting cart items: cart_id={cart_id}")

        db = self._get_session()
        try:
            cart = db.query(AbandonedCart).filter(AbandonedCart.cart_id == cart_id).first()

            if not cart:
                self.logger.warning(f"Cart not found: {cart_id}")
                return []

            items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

            self.logger.debug(f"Found {len(items)} items for cart {cart_id}")
            return items

        except Exception as e:
            self.logger.error(f"Error getting cart items: {str(e)}", exc_info=True)
            raise
        finally:
            if self._should_close_session():
                db.close()

    def get_recovery_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get cart recovery analytics for the specified time period.

        Args:
            days: Number of days to look back (default: 30)

        Returns:
            Dictionary with analytics data
        """
        self.logger.info(f"Getting recovery analytics for last {days} days")

        db = self._get_session()
        try:
            since_date = datetime.utcnow() - timedelta(days=days)

            # Get counts by status
            total_carts = db.query(AbandonedCart).filter(
                AbandonedCart.created_at >= since_date
            ).count()

            abandoned_carts = db.query(AbandonedCart).filter(
                and_(
                    AbandonedCart.created_at >= since_date,
                    AbandonedCart.status == "abandoned"
                )
            ).count()

            recovered_carts = db.query(AbandonedCart).filter(
                and_(
                    AbandonedCart.created_at >= since_date,
                    AbandonedCart.status == "recovered"
                )
            ).count()

            # Calculate recovery rate
            recovery_rate = (recovered_carts / abandoned_carts * 100) if abandoned_carts > 0 else 0

            # Get total recovered revenue
            recovered_revenue = db.query(AbandonedCart).filter(
                and_(
                    AbandonedCart.created_at >= since_date,
                    AbandonedCart.status == "recovered"
                )
            ).with_entities(AbandonedCart.total_value).all()

            total_recovered_value = sum(float(cart[0] or 0) for cart in recovered_revenue)

            # Email engagement metrics
            total_emails_sent = db.query(CartRecoveryEmail).join(AbandonedCart).filter(
                and_(
                    AbandonedCart.created_at >= since_date,
                    CartRecoveryEmail.status == "sent"
                )
            ).count()

            emails_opened = db.query(CartRecoveryEmail).join(AbandonedCart).filter(
                and_(
                    AbandonedCart.created_at >= since_date,
                    CartRecoveryEmail.opened_at.isnot(None)
                )
            ).count()

            emails_clicked = db.query(CartRecoveryEmail).join(AbandonedCart).filter(
                and_(
                    AbandonedCart.created_at >= since_date,
                    CartRecoveryEmail.clicked_at.isnot(None)
                )
            ).count()

            # Calculate rates
            open_rate = (emails_opened / total_emails_sent * 100) if total_emails_sent > 0 else 0
            click_rate = (emails_clicked / total_emails_sent * 100) if total_emails_sent > 0 else 0

            analytics = {
                "period_days": days,
                "total_carts": total_carts,
                "abandoned_carts": abandoned_carts,
                "recovered_carts": recovered_carts,
                "recovery_rate": round(recovery_rate, 2),
                "total_recovered_value": round(total_recovered_value, 2),
                "email_stats": {
                    "total_sent": total_emails_sent,
                    "total_opened": emails_opened,
                    "total_clicked": emails_clicked,
                    "open_rate": round(open_rate, 2),
                    "click_rate": round(click_rate, 2)
                }
            }

            self.logger.info(f"Analytics generated: recovery_rate={recovery_rate:.2f}%, recovered_value=${total_recovered_value:.2f}")
            return analytics

        except Exception as e:
            self.logger.error(f"Error getting recovery analytics: {str(e)}", exc_info=True)
            raise
        finally:
            if self._should_close_session():
                db.close()
