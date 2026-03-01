"""
Clerk webhook handler for syncing users to Klaviyo.

This module handles incoming webhooks from Clerk to sync user data
to Klaviyo for email marketing automation.
"""

from typing import Dict, Any, Optional
import hmac
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ClerkWebhookHandler:
    """Handle Clerk webhooks for user sync to Klaviyo"""

    def __init__(self, webhook_secret: str, klaviyo_client: Any):
        """
        Initialize the Clerk webhook handler.

        Args:
            webhook_secret: Secret key for verifying webhook signatures
            klaviyo_client: KlaviyoClient instance for API calls
        """
        self.webhook_secret = webhook_secret
        self.klaviyo = klaviyo_client

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Clerk.

        Args:
            payload: Raw webhook payload bytes
            signature: Signature from webhook headers

        Returns:
            True if signature is valid, False otherwise
        """
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def handle_user_created(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync new Clerk user to Klaviyo.

        Args:
            user_data: User data from Clerk webhook

        Returns:
            Result of Klaviyo profile creation
        """
        try:
            # Extract email from Clerk user data
            email_addresses = user_data.get('email_addresses', [])
            if not email_addresses:
                logger.warning(f"No email addresses for Clerk user {user_data.get('id')}")
                return {"error": "No email address found"}

            primary_email = email_addresses[0].get('email_address')

            # Extract metadata
            public_metadata = user_data.get('public_metadata', {})

            # Create Klaviyo profile
            profile = {
                'external_id': user_data['id'],  # Clerk user.id
                'email': primary_email,
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'properties': {
                    'source': public_metadata.get('source', 'scratch_and_win'),
                    'game_preference': public_metadata.get('gamePreference'),
                    'prize_code': public_metadata.get('prizeCode'),
                    'prize_type': public_metadata.get('prizeType'),
                    'signup_timestamp': datetime.utcnow().isoformat(),
                    'clerk_user_id': user_data['id']
                }
            }

            result = self.klaviyo.create_or_update_profile(profile)

            # Track signup event for funnel analytics
            self._track_signup_event(user_data, profile)

            logger.info(f"Successfully synced Clerk user {user_data['id']} to Klaviyo")
            return result

        except Exception as e:
            logger.error(f"Error syncing Clerk user to Klaviyo: {str(e)}")
            return {"error": str(e)}

    def handle_user_updated(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing Klaviyo profile when Clerk user is updated.

        Args:
            user_data: Updated user data from Clerk webhook

        Returns:
            Result of Klaviyo profile update
        """
        try:
            email_addresses = user_data.get('email_addresses', [])
            if not email_addresses:
                return {"error": "No email address found"}

            primary_email = email_addresses[0].get('email_address')
            public_metadata = user_data.get('public_metadata', {})

            # Update Klaviyo profile
            profile = {
                'external_id': user_data['id'],
                'email': primary_email,
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'properties': {
                    'game_preference': public_metadata.get('gamePreference'),
                    'prize_code': public_metadata.get('prizeCode'),
                    'prize_type': public_metadata.get('prizeType'),
                    'last_updated': datetime.utcnow().isoformat()
                }
            }

            result = self.klaviyo.create_or_update_profile(profile)
            logger.info(f"Successfully updated Klaviyo profile for Clerk user {user_data['id']}")
            return result

        except Exception as e:
            logger.error(f"Error updating Klaviyo profile: {str(e)}")
            return {"error": str(e)}

    def handle_session_created(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track user login events in Klaviyo.

        Args:
            session_data: Session data from Clerk webhook

        Returns:
            Result of event tracking
        """
        try:
            user_id = session_data.get('user_id')
            if not user_id:
                return {"error": "No user_id in session data"}

            # Track login event
            event = {
                'event': 'User Login',
                'customer_properties': {
                    'external_id': user_id
                },
                'properties': {
                    'session_id': session_data.get('id'),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }

            result = self.klaviyo.track_event(event)
            logger.info(f"Tracked login event for user {user_id}")
            return result

        except Exception as e:
            logger.error(f"Error tracking login event: {str(e)}")
            return {"error": str(e)}

    def _track_signup_event(self, user_data: Dict[str, Any], profile: Dict[str, Any]) -> None:
        """
        Track signup event for funnel analytics.

        Args:
            user_data: Original Clerk user data
            profile: Created Klaviyo profile
        """
        try:
            public_metadata = user_data.get('public_metadata', {})

            # Track the signup event
            event = {
                'event': 'Scratch Win Signup',
                'customer_properties': {
                    'email': profile['email'],
                    'external_id': user_data['id']
                },
                'properties': {
                    'source': public_metadata.get('source', 'scratch_and_win'),
                    'prize_type': public_metadata.get('prizeType'),
                    'prize_code': public_metadata.get('prizeCode'),
                    'game_preference': public_metadata.get('gamePreference'),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }

            self.klaviyo.track_event(event)

            # If user came from scratch-win, track funnel step
            if public_metadata.get('source') == 'scratch_win':
                funnel_event = {
                    'event': 'Funnel Step - Scratch Win Conversion',
                    'customer_properties': {
                        'email': profile['email'],
                        'external_id': user_data['id']
                    },
                    'properties': {
                        'step': 'signup',
                        'prize_type': public_metadata.get('prizeType'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }
                self.klaviyo.track_event(funnel_event)

        except Exception as e:
            logger.error(f"Error tracking signup event: {str(e)}")

    def handle_webhook(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route webhook events to appropriate handlers.

        Args:
            event_type: Type of Clerk webhook event
            data: Webhook payload data

        Returns:
            Result of handling the webhook
        """
        handlers = {
            'user.created': self.handle_user_created,
            'user.updated': self.handle_user_updated,
            'session.created': self.handle_session_created
        }

        handler = handlers.get(event_type)
        if handler:
            return handler(data)
        else:
            logger.info(f"No handler for webhook event type: {event_type}")
            return {"status": "ignored", "event_type": event_type}