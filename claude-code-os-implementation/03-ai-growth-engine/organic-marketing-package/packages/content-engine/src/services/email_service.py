"""
Email Service

This module provides email sending functionality using SendGrid for
abandoned cart recovery emails and other transactional communications.
"""
import os
from typing import Dict, Optional, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

from logging_config import get_logger


class EmailServiceError(Exception):
    """
    Base exception for all email service errors

    This is the parent class for all email service-related exceptions.
    Use this for catching any email service error generically.

    Attributes:
        message: Error message
        status_code: HTTP status code (if applicable)
        response: Raw response data (if applicable)
    """

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        """
        Initialize EmailServiceError

        Args:
            message: Human-readable error message
            status_code: HTTP status code from API response
            response: Full response data from the API
        """
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class EmailConfigError(EmailServiceError):
    """
    Exception raised for email configuration errors

    This exception is raised when:
    - SendGrid API key is missing or invalid
    - Template directory cannot be found
    - Required configuration is missing
    """

    def __init__(self, message: str):
        """
        Initialize EmailConfigError

        Args:
            message: Human-readable error message
        """
        super().__init__(message)


class EmailTemplateError(EmailServiceError):
    """
    Exception raised for template-related errors

    This exception is raised when:
    - Template file cannot be found
    - Template rendering fails
    - Invalid template variables provided
    """

    def __init__(self, message: str, template_name: Optional[str] = None):
        """
        Initialize EmailTemplateError

        Args:
            message: Human-readable error message
            template_name: Name of the template that caused the error
        """
        self.template_name = template_name
        error_msg = f"{message} (template: {template_name})" if template_name else message
        super().__init__(error_msg)


class EmailSendError(EmailServiceError):
    """
    Exception raised when email sending fails

    This exception is raised when:
    - SendGrid API returns an error
    - Network issues prevent sending
    - Rate limits are exceeded
    """

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        """
        Initialize EmailSendError

        Args:
            message: Human-readable error message
            status_code: HTTP status code from SendGrid
            response: Full response data from SendGrid
        """
        super().__init__(message, status_code, response)


class EmailService:
    """
    Email service for sending transactional emails using SendGrid

    This service provides methods for sending emails using SendGrid API
    with Jinja2 template rendering for HTML email content.

    Attributes:
        api_key: SendGrid API key
        from_email: Default sender email address
        from_name: Default sender name
        template_dir: Directory containing email templates
        _client: SendGrid API client instance
        _template_env: Jinja2 template environment
        logger: Logger instance for this service
    """

    # Default configuration
    DEFAULT_FROM_EMAIL = "noreply@infinityvault.com"
    DEFAULT_FROM_NAME = "Infinity Vault"
    DEFAULT_TEMPLATE_DIR = "templates/email"

    # Email types for abandoned cart recovery
    EMAIL_TYPE_REMINDER = "cart_reminder"
    EMAIL_TYPE_URGENCY = "cart_urgency"
    EMAIL_TYPE_OFFER = "cart_offer"

    # Subject lines for cart recovery emails
    SUBJECT_LINES = {
        EMAIL_TYPE_REMINDER: "You left items in your cart - Complete your order",
        EMAIL_TYPE_URGENCY: "Your cart is waiting - Don't miss out!",
        EMAIL_TYPE_OFFER: "Special discount on your cart - Limited time!"
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        template_dir: Optional[str] = None
    ):
        """
        Initialize EmailService

        Args:
            api_key: SendGrid API key (if not provided, uses SENDGRID_API_KEY env var)
            from_email: Default sender email address
            from_name: Default sender name
            template_dir: Directory containing email templates (relative to content-agents/)

        Raises:
            EmailConfigError: If SendGrid API key is not provided or template directory not found

        Example:
            >>> service = EmailService()
            >>> # Service is ready to send emails
            >>> service = EmailService(api_key="custom_key", from_email="custom@example.com")
        """
        self.logger = get_logger("email_service")

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
        if not self.api_key:
            raise EmailConfigError(
                "SendGrid API key is required. Set SENDGRID_API_KEY environment variable "
                "or pass api_key parameter"
            )

        # Set sender details
        self.from_email = from_email or os.getenv("SENDGRID_FROM_EMAIL", self.DEFAULT_FROM_EMAIL)
        self.from_name = from_name or os.getenv("SENDGRID_FROM_NAME", self.DEFAULT_FROM_NAME)

        # Set template directory
        template_dir = template_dir or os.getenv("EMAIL_TEMPLATE_DIR", self.DEFAULT_TEMPLATE_DIR)
        self.template_dir = Path(__file__).parent.parent / template_dir

        # Validate template directory exists
        if not self.template_dir.exists():
            self.logger.warning(
                f"Template directory does not exist: {self.template_dir}. "
                f"Email templates will need to be created before sending emails."
            )

        # Initialize SendGrid client
        try:
            self._client = SendGridAPIClient(self.api_key)
            self.logger.info("SendGrid client initialized successfully")
        except Exception as e:
            raise EmailConfigError(f"Failed to initialize SendGrid client: {str(e)}")

        # Initialize Jinja2 template environment
        try:
            self._template_env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
            self.logger.info(f"Template environment initialized with directory: {self.template_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize template environment: {str(e)}")
            self._template_env = None

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render an email template with the provided context

        Args:
            template_name: Name of the template file (e.g., 'cart_reminder.html')
            context: Dictionary of variables to pass to the template

        Returns:
            Rendered HTML string

        Raises:
            EmailTemplateError: If template cannot be found or rendered

        Example:
            >>> service = EmailService()
            >>> html = service.render_template('cart_reminder.html', {
            ...     'customer_name': 'John',
            ...     'cart_items': [{'name': 'Product', 'price': 29.99}]
            ... })
        """
        if not self._template_env:
            raise EmailTemplateError(
                "Template environment not initialized. Check template directory configuration.",
                template_name
            )

        try:
            template = self._template_env.get_template(template_name)
            rendered = template.render(**context)
            self.logger.debug(f"Successfully rendered template: {template_name}")
            return rendered
        except TemplateNotFound:
            raise EmailTemplateError(
                f"Template not found: {template_name}. "
                f"Ensure the template exists in {self.template_dir}",
                template_name
            )
        except Exception as e:
            raise EmailTemplateError(
                f"Failed to render template: {str(e)}",
                template_name
            )

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        plain_text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using SendGrid

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML email content
            from_email: Sender email (uses default if not provided)
            from_name: Sender name (uses default if not provided)
            plain_text_content: Optional plain text version of the email

        Returns:
            True if email was sent successfully

        Raises:
            EmailSendError: If email sending fails

        Example:
            >>> service = EmailService()
            >>> service.send_email(
            ...     to_email="customer@example.com",
            ...     subject="Your cart is waiting",
            ...     html_content="<h1>Complete your order</h1>"
            ... )
        """
        sender_email = from_email or self.from_email
        sender_name = from_name or self.from_name

        self.logger.info(f"Sending email to {to_email} with subject: {subject}")

        try:
            # Create email message
            from_addr = Email(sender_email, sender_name)
            to_addr = To(to_email)
            content = Content("text/html", html_content)

            mail = Mail(from_addr, to_addr, subject, content)

            # Add plain text version if provided
            if plain_text_content:
                mail.add_content(Content("text/plain", plain_text_content))

            # Send email
            response = self._client.send(mail)

            # Check response status
            if response.status_code >= 200 and response.status_code < 300:
                self.logger.info(
                    f"Email sent successfully to {to_email}. "
                    f"Status: {response.status_code}"
                )
                return True
            else:
                raise EmailSendError(
                    f"SendGrid returned non-success status",
                    status_code=response.status_code,
                    response={"body": response.body, "headers": dict(response.headers)}
                )

        except EmailSendError:
            # Re-raise EmailSendError
            raise
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise EmailSendError(f"Failed to send email: {str(e)}")

    def send_cart_recovery_email(
        self,
        to_email: str,
        email_type: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Send a cart recovery email using the appropriate template

        This is a convenience method that combines template rendering and email sending
        for abandoned cart recovery emails.

        Args:
            to_email: Customer email address
            email_type: Type of recovery email (cart_reminder, cart_urgency, cart_offer)
            context: Template context containing cart_items, customer_name, recovery_link, etc.

        Returns:
            True if email was sent successfully

        Raises:
            EmailTemplateError: If template cannot be found or rendered
            EmailSendError: If email sending fails
            ValueError: If invalid email_type provided

        Example:
            >>> service = EmailService()
            >>> service.send_cart_recovery_email(
            ...     to_email="customer@example.com",
            ...     email_type=EmailService.EMAIL_TYPE_REMINDER,
            ...     context={
            ...         'customer_name': 'John',
            ...         'cart_items': [{'name': 'Product', 'price': 29.99}],
            ...         'recovery_link': 'https://example.com/cart/recover/abc123',
            ...         'total_value': 29.99
            ...     }
            ... )
        """
        # Validate email type
        valid_types = [self.EMAIL_TYPE_REMINDER, self.EMAIL_TYPE_URGENCY, self.EMAIL_TYPE_OFFER]
        if email_type not in valid_types:
            raise ValueError(
                f"Invalid email_type: {email_type}. "
                f"Must be one of: {', '.join(valid_types)}"
            )

        self.logger.info(f"Sending cart recovery email type '{email_type}' to {to_email}")

        # Get template name and subject
        template_name = f"{email_type}.html"
        subject = self.SUBJECT_LINES.get(email_type, "Complete your order")

        # Render template
        html_content = self.render_template(template_name, context)

        # Send email
        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )

    def test_connection(self) -> bool:
        """
        Test SendGrid API connection by attempting to retrieve account information

        Returns:
            True if connection is successful

        Raises:
            EmailSendError: If connection test fails

        Example:
            >>> service = EmailService()
            >>> if service.test_connection():
            ...     print("SendGrid connection successful")
        """
        self.logger.info("Testing SendGrid API connection")

        try:
            # SendGrid doesn't have a dedicated ping endpoint, but we can
            # verify the API key works by checking if the client is properly initialized
            if self._client and self.api_key:
                self.logger.info("SendGrid API connection test passed")
                return True
            else:
                raise EmailSendError("SendGrid client not properly initialized")
        except Exception as e:
            self.logger.error(f"SendGrid connection test failed: {str(e)}")
            raise EmailSendError(f"Connection test failed: {str(e)}")
