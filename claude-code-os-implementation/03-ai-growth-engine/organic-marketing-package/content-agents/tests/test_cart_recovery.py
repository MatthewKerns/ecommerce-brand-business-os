"""
End-to-end integration tests for abandoned cart recovery system.

Tests cover:
- Cart tracking via API
- Cart abandonment detection
- Recovery email scheduling and sending
- Recovery link handling
- Analytics endpoints
- TikTok Shop webhook integration
- Full cart recovery flow
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock, call
from datetime import datetime, timedelta
from pathlib import Path
from freezegun import freezegun
import json

from api.main import app
from services.cart_service import CartService
from services.email_service import EmailService, EmailServiceError
from tasks.cart_recovery import (
    process_abandoned_carts,
    send_recovery_email,
    schedule_recovery_sequence
)
from database.models import AbandonedCart, CartItem, CartRecoveryEmail
from database.connection import get_db_session


class TestCartTrackingAPI:
    """Test suite for cart tracking API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        session = get_db_session()
        yield session
        # Cleanup: rollback any uncommitted changes
        session.rollback()
        # Cleanup: delete test data
        session.query(CartRecoveryEmail).delete()
        session.query(CartItem).delete()
        session.query(AbandonedCart).delete()
        session.commit()
        session.close()

    def test_track_cart_success(self, client, db_session):
        """Test successful cart tracking via API"""
        request_data = {
            "email": "customer@example.com",
            "cart_items": [
                {
                    "product_id": "prod-123",
                    "name": "Tactical EDC Backpack",
                    "price": 89.99,
                    "quantity": 1,
                    "image_url": "https://example.com/backpack.jpg"
                },
                {
                    "product_id": "prod-456",
                    "name": "Multi-Tool Kit",
                    "price": 45.50,
                    "quantity": 2
                }
            ],
            "source": "website"
        }

        response = client.post("/api/cart/track", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "cart_id" in data
        assert data["status"] == "active"
        assert data["total_value"] == 180.99  # 89.99 + (45.50 * 2)

        # Verify cart was created in database
        cart = db_session.query(AbandonedCart).filter_by(cart_id=data["cart_id"]).first()
        assert cart is not None
        assert cart.email == "customer@example.com"
        assert cart.platform == "website"
        assert float(cart.total_value) == 180.99

        # Verify cart items were created
        items = db_session.query(CartItem).filter_by(cart_id=cart.id).all()
        assert len(items) == 2

    def test_track_cart_minimal_fields(self, client, db_session):
        """Test cart tracking with minimal required fields"""
        request_data = {
            "email": "minimal@example.com",
            "cart_items": [
                {
                    "product_id": "prod-789",
                    "name": "Test Product",
                    "price": 29.99,
                    "quantity": 1
                }
            ]
        }

        response = client.post("/api/cart/track", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should use default values
        assert data["status"] == "active"

        # Verify defaults in database
        cart = db_session.query(AbandonedCart).filter_by(cart_id=data["cart_id"]).first()
        assert cart.platform == "website"  # Default platform

    def test_track_cart_update_existing(self, client, db_session):
        """Test updating an existing cart"""
        cart_id = "test_cart_123"

        # First request - create cart
        request_data = {
            "email": "customer@example.com",
            "cart_items": [
                {
                    "product_id": "prod-1",
                    "name": "Product 1",
                    "price": 50.00,
                    "quantity": 1
                }
            ],
            "cart_id": cart_id
        }

        response1 = client.post("/api/cart/track", json=request_data)
        assert response1.status_code == 200

        # Second request - update cart
        request_data["cart_items"].append({
            "product_id": "prod-2",
            "name": "Product 2",
            "price": 75.00,
            "quantity": 1
        })

        response2 = client.post("/api/cart/track", json=request_data)
        assert response2.status_code == 200
        data = response2.json()

        assert data["total_value"] == 125.00  # Updated total

        # Verify only one cart exists
        carts = db_session.query(AbandonedCart).filter_by(cart_id=cart_id).all()
        assert len(carts) == 1

        # Verify items were updated
        items = db_session.query(CartItem).filter_by(cart_id=carts[0].id).all()
        assert len(items) == 2

    def test_track_cart_invalid_empty_items(self, client):
        """Test validation error for empty cart items"""
        request_data = {
            "email": "customer@example.com",
            "cart_items": []  # Empty items list
        }

        response = client.post("/api/cart/track", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_track_cart_invalid_email(self, client):
        """Test validation error for invalid email"""
        request_data = {
            "email": "not-an-email",
            "cart_items": [
                {
                    "product_id": "prod-1",
                    "name": "Product",
                    "price": 50.00
                }
            ]
        }

        response = client.post("/api/cart/track", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_track_cart_tiktok_source(self, client, db_session):
        """Test cart tracking from TikTok Shop"""
        request_data = {
            "email": "tiktok@example.com",
            "cart_items": [
                {
                    "product_id": "tiktok-prod-123",
                    "name": "TikTok Product",
                    "price": 39.99,
                    "quantity": 1
                }
            ],
            "source": "tiktok_shop"
        }

        response = client.post("/api/cart/track", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify platform in database
        cart = db_session.query(AbandonedCart).filter_by(cart_id=data["cart_id"]).first()
        assert cart.platform == "tiktok_shop"


class TestCartRecoveryFlow:
    """Test suite for cart recovery link handling"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        session = get_db_session()
        yield session
        # Cleanup
        session.rollback()
        session.query(CartRecoveryEmail).delete()
        session.query(CartItem).delete()
        session.query(AbandonedCart).delete()
        session.commit()
        session.close()

    @pytest.fixture
    def abandoned_cart(self, db_session):
        """Create an abandoned cart for testing"""
        cart = AbandonedCart(
            cart_id="test_abandoned_cart",
            email="abandoned@example.com",
            platform="website",
            cart_data=json.dumps({"items": []}),
            cart_url="https://example.com/cart/test_abandoned_cart",
            total_value=99.99,
            currency="USD",
            status="abandoned",
            abandoned_at=datetime.utcnow()
        )
        db_session.add(cart)
        db_session.commit()
        db_session.refresh(cart)
        return cart

    def test_recover_cart_success(self, client, abandoned_cart, db_session):
        """Test successful cart recovery via recovery link"""
        response = client.get(f"/api/cart/recover/{abandoned_cart.cart_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["cart_id"] == abandoned_cart.cart_id
        assert data["status"] == "recovered"
        assert data["cart_url"] == abandoned_cart.cart_url
        assert "recovered successfully" in data["message"].lower()

        # Verify cart status was updated in database
        db_session.refresh(abandoned_cart)
        assert abandoned_cart.status == "recovered"
        assert abandoned_cart.recovered_at is not None

    def test_recover_cart_not_found(self, client):
        """Test recovery attempt for non-existent cart"""
        response = client.get("/api/cart/recover/nonexistent_cart_id")

        assert response.status_code == 404
        data = response.json()

        assert "error" in data["detail"]
        assert data["detail"]["error"] == "NotFound"

    def test_get_cart_details(self, client, abandoned_cart, db_session):
        """Test retrieving cart details"""
        # Add cart items
        item = CartItem(
            cart_id=abandoned_cart.id,
            product_id="prod-123",
            product_name="Test Product",
            price=99.99,
            quantity=1
        )
        db_session.add(item)
        db_session.commit()

        response = client.get(f"/api/cart/{abandoned_cart.cart_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["cart_id"] == abandoned_cart.cart_id
        assert data["email"] == abandoned_cart.email
        assert data["status"] == "abandoned"
        assert len(data["items"]) == 1
        assert data["items"][0]["product_name"] == "Test Product"


class TestCartAnalytics:
    """Test suite for cart analytics endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        session = get_db_session()
        yield session
        # Cleanup
        session.rollback()
        session.query(CartRecoveryEmail).delete()
        session.query(CartItem).delete()
        session.query(AbandonedCart).delete()
        session.commit()
        session.close()

    @pytest.fixture
    def sample_carts(self, db_session):
        """Create sample carts for analytics testing"""
        carts = []

        # Active cart
        carts.append(AbandonedCart(
            cart_id="active_cart_1",
            email="active@example.com",
            platform="website",
            cart_data=json.dumps({"items": []}),
            total_value=50.00,
            status="active"
        ))

        # Abandoned cart
        carts.append(AbandonedCart(
            cart_id="abandoned_cart_1",
            email="abandoned1@example.com",
            platform="website",
            cart_data=json.dumps({"items": []}),
            total_value=100.00,
            status="abandoned",
            abandoned_at=datetime.utcnow() - timedelta(hours=1)
        ))

        # Recovered cart
        carts.append(AbandonedCart(
            cart_id="recovered_cart_1",
            email="recovered@example.com",
            platform="website",
            cart_data=json.dumps({"items": []}),
            total_value=150.00,
            status="recovered",
            abandoned_at=datetime.utcnow() - timedelta(days=1),
            recovered_at=datetime.utcnow() - timedelta(hours=12)
        ))

        for cart in carts:
            db_session.add(cart)

        db_session.commit()

        # Add recovery email for recovered cart
        email_record = CartRecoveryEmail(
            cart_id=carts[2].id,
            sequence_number=1,
            email_type="reminder",
            status="sent",
            sent_at=datetime.utcnow() - timedelta(days=1),
            opened_at=datetime.utcnow() - timedelta(hours=23),
            clicked_at=datetime.utcnow() - timedelta(hours=12)
        )
        db_session.add(email_record)
        db_session.commit()

        return carts

    def test_get_analytics_success(self, client, sample_carts):
        """Test successful analytics retrieval"""
        response = client.get("/api/cart/analytics?days=30")

        assert response.status_code == 200
        data = response.json()

        assert "request_id" in data
        assert "period_days" in data
        assert "total_carts" in data
        assert "abandoned_carts" in data
        assert "recovered_carts" in data
        assert "recovery_rate" in data
        assert "total_recovered_value" in data
        assert "email_stats" in data

        assert data["period_days"] == 30
        assert data["total_carts"] >= 3
        assert data["abandoned_carts"] >= 1
        assert data["recovered_carts"] >= 1

    def test_get_analytics_custom_period(self, client, sample_carts):
        """Test analytics with custom time period"""
        response = client.get("/api/cart/analytics?days=7")

        assert response.status_code == 200
        data = response.json()

        assert data["period_days"] == 7

    def test_get_analytics_invalid_period(self, client):
        """Test analytics with invalid period"""
        response = client.get("/api/cart/analytics?days=500")  # Exceeds max

        assert response.status_code == 400
        data = response.json()

        assert "error" in data["detail"]
        assert data["detail"]["error"] == "ValidationError"


class TestCartService:
    """Test suite for CartService business logic"""

    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        session = get_db_session()
        yield session
        # Cleanup
        session.rollback()
        session.query(CartRecoveryEmail).delete()
        session.query(CartItem).delete()
        session.query(AbandonedCart).delete()
        session.commit()
        session.close()

    @pytest.fixture
    def cart_service(self, db_session):
        """Create CartService instance with test session"""
        return CartService(db=db_session)

    def test_track_cart_event(self, cart_service, db_session):
        """Test tracking a cart event"""
        cart_items = [
            {
                "product_id": "prod-1",
                "name": "Product 1",
                "price": 50.00,
                "quantity": 1,
                "image_url": "https://example.com/prod1.jpg"
            }
        ]

        cart = cart_service.track_cart_event(
            cart_id="service_test_cart",
            email="service@example.com",
            cart_items=cart_items,
            platform="website"
        )

        assert cart is not None
        assert cart.cart_id == "service_test_cart"
        assert cart.email == "service@example.com"
        assert float(cart.total_value) == 50.00

    def test_mark_abandoned(self, cart_service, db_session):
        """Test marking a cart as abandoned"""
        # Create active cart
        cart_items = [{"product_id": "prod-1", "name": "Product 1", "price": 50.00, "quantity": 1}]
        cart = cart_service.track_cart_event(
            cart_id="mark_abandoned_test",
            email="test@example.com",
            cart_items=cart_items
        )

        assert cart.status == "active"

        # Mark as abandoned
        abandoned_cart = cart_service.mark_abandoned(cart.cart_id)

        assert abandoned_cart.status == "abandoned"
        assert abandoned_cart.abandoned_at is not None

    def test_recover_cart(self, cart_service, db_session):
        """Test recovering a cart"""
        # Create and abandon cart
        cart_items = [{"product_id": "prod-1", "name": "Product 1", "price": 50.00, "quantity": 1}]
        cart = cart_service.track_cart_event(
            cart_id="recover_test",
            email="test@example.com",
            cart_items=cart_items
        )
        cart_service.mark_abandoned(cart.cart_id)

        # Recover cart
        recovered_cart = cart_service.recover_cart(cart.cart_id)

        assert recovered_cart.status == "recovered"
        assert recovered_cart.recovered_at is not None

    def test_get_abandoned_carts(self, cart_service, db_session):
        """Test retrieving abandoned carts"""
        # Create cart that's old enough to be abandoned
        old_time = datetime.utcnow() - timedelta(minutes=35)

        cart = AbandonedCart(
            cart_id="old_cart",
            email="old@example.com",
            platform="website",
            cart_data=json.dumps({"items": []}),
            total_value=50.00,
            status="active",
            created_at=old_time
        )
        db_session.add(cart)
        db_session.commit()

        # Get abandoned carts
        abandoned_carts = cart_service.get_abandoned_carts(
            min_age_minutes=30,
            max_age_hours=72
        )

        assert len(abandoned_carts) >= 1
        assert any(c.cart_id == "old_cart" for c in abandoned_carts)


class TestCeleryTasks:
    """Test suite for Celery background tasks"""

    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        session = get_db_session()
        yield session
        # Cleanup
        session.rollback()
        session.query(CartRecoveryEmail).delete()
        session.query(CartItem).delete()
        session.query(AbandonedCart).delete()
        session.commit()
        session.close()

    @pytest.fixture
    def old_cart(self, db_session):
        """Create an old cart for abandoned cart processing"""
        old_time = datetime.utcnow() - timedelta(minutes=35)

        cart = AbandonedCart(
            cart_id="old_cart_task",
            email="oldcart@example.com",
            platform="website",
            cart_data=json.dumps({"items": [{"product_id": "prod-1", "name": "Product", "price": 50.00}]}),
            total_value=50.00,
            status="active",
            created_at=old_time
        )
        db_session.add(cart)

        # Add cart item
        item = CartItem(
            cart_id=None,  # Will be set after cart is added
            product_id="prod-1",
            product_name="Product",
            price=50.00,
            quantity=1
        )
        db_session.flush()
        item.cart_id = cart.id
        db_session.add(item)

        db_session.commit()
        db_session.refresh(cart)
        return cart

    @patch('tasks.cart_recovery.schedule_recovery_sequence.delay')
    def test_process_abandoned_carts_task(self, mock_schedule, old_cart, db_session):
        """Test process_abandoned_carts Celery task"""
        # Run the task
        result = process_abandoned_carts()

        assert result["carts_processed"] >= 1
        assert result["sequences_scheduled"] >= 1
        assert result["errors"] == 0

        # Verify cart was marked as abandoned
        db_session.refresh(old_cart)
        assert old_cart.status == "abandoned"

        # Verify scheduling was called
        assert mock_schedule.called

    @patch('tasks.cart_recovery.send_recovery_email.apply_async')
    def test_schedule_recovery_sequence_task(self, mock_send_email, old_cart, db_session):
        """Test schedule_recovery_sequence Celery task"""
        # Mark cart as abandoned first
        old_cart.status = "abandoned"
        old_cart.abandoned_at = datetime.utcnow()
        db_session.commit()

        # Run the task
        result = schedule_recovery_sequence(old_cart.cart_id)

        assert result["success"] is True
        assert len(result["emails_scheduled"]) == 3
        assert "reminder" in result["emails_scheduled"]
        assert "urgency" in result["emails_scheduled"]
        assert "offer" in result["emails_scheduled"]

        # Verify emails were scheduled
        assert mock_send_email.call_count == 3

    @patch.object(EmailService, 'send_cart_recovery_email')
    def test_send_recovery_email_task(self, mock_send, old_cart, db_session):
        """Test send_recovery_email Celery task"""
        # Mark cart as abandoned
        old_cart.status = "abandoned"
        old_cart.abandoned_at = datetime.utcnow()
        db_session.commit()

        # Add cart item
        item = CartItem(
            cart_id=old_cart.id,
            product_id="prod-1",
            product_name="Product",
            price=50.00,
            quantity=1
        )
        db_session.add(item)
        db_session.commit()

        # Mock successful email send
        mock_send.return_value = None

        # Run the task
        result = send_recovery_email(old_cart.cart_id, "reminder")

        assert result["success"] is True
        assert result["cart_id"] == old_cart.cart_id
        assert result["email_type"] == "reminder"

        # Verify email record was created
        email_record = db_session.query(CartRecoveryEmail).filter_by(
            cart_id=old_cart.id,
            email_type="reminder"
        ).first()

        assert email_record is not None
        assert email_record.status == "sent"
        assert email_record.sent_at is not None


class TestTikTokWebhook:
    """Test suite for TikTok Shop webhook integration"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        session = get_db_session()
        yield session
        # Cleanup
        session.rollback()
        session.query(CartRecoveryEmail).delete()
        session.query(CartItem).delete()
        session.query(AbandonedCart).delete()
        session.commit()
        session.close()

    @patch.dict('os.environ', {'TIKTOK_SHOP_APP_SECRET': 'test_secret_key'})
    @patch('integrations.tiktok_shop.webhooks.TikTokShopWebhookHandler.validate_signature')
    @patch('integrations.tiktok_shop.webhooks.TikTokShopWebhookHandler.parse_payload')
    @patch('integrations.tiktok_shop.webhooks.TikTokShopWebhookHandler.handle_cart_event')
    def test_tiktok_webhook_cart_updated(
        self,
        mock_handle_cart,
        mock_parse,
        mock_validate,
        client,
        db_session
    ):
        """Test TikTok Shop cart_updated webhook"""
        # Mock webhook handler methods
        mock_validate.return_value = True
        mock_parse.return_value = {
            "event_type": "cart_updated"
        }
        mock_handle_cart.return_value = {
            "cart_id": "tiktok_cart_123",
            "user_email": "tiktok@example.com",
            "user_id": "tiktok_user_1",
            "items": [
                {
                    "product_id": "tiktok-prod-1",
                    "name": "TikTok Product",
                    "price": 39.99,
                    "quantity": 1
                }
            ],
            "cart_url": "https://tiktok.com/cart/123"
        }

        # Send webhook request
        payload = {
            "event_type": "cart_updated",
            "cart_data": {
                "user_email": "tiktok@example.com",
                "items": []
            }
        }

        response = client.post(
            "/api/cart/webhook/tiktok",
            json=payload,
            headers={
                "X-TikTok-Signature": "test_signature",
                "X-TikTok-Timestamp": str(int(datetime.utcnow().timestamp()))
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["event_type"] == "cart_updated"
        assert "cart_id" in data

        # Verify cart was created
        cart = db_session.query(AbandonedCart).filter_by(cart_id=data["cart_id"]).first()
        assert cart is not None
        assert cart.platform == "tiktok_shop"


class TestEndToEndCartRecoveryFlow:
    """End-to-end test for complete cart recovery flow"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def db_session(self):
        """Create test database session"""
        session = get_db_session()
        yield session
        # Cleanup
        session.rollback()
        session.query(CartRecoveryEmail).delete()
        session.query(CartItem).delete()
        session.query(AbandonedCart).delete()
        session.commit()
        session.close()

    @freezegun.freeze_time("2025-01-01 12:00:00")
    @patch.object(EmailService, 'send_cart_recovery_email')
    @patch('tasks.cart_recovery.send_recovery_email.apply_async')
    def test_e2e_cart_recovery_flow(self, mock_send_email_task, mock_email_service, client, db_session):
        """
        Test complete end-to-end cart recovery flow:
        1. Customer creates cart
        2. Cart is abandoned (30+ minutes)
        3. Recovery email sequence is scheduled
        4. First email is sent
        5. Customer clicks recovery link
        6. Cart is recovered
        7. Analytics show recovery
        """
        # Step 1: Customer creates cart via API
        cart_data = {
            "email": "e2e@example.com",
            "cart_items": [
                {
                    "product_id": "e2e-prod-1",
                    "name": "E2E Test Product",
                    "price": 99.99,
                    "quantity": 1,
                    "image_url": "https://example.com/product.jpg"
                }
            ],
            "source": "website"
        }

        response = client.post("/api/cart/track", json=cart_data)
        assert response.status_code == 200
        cart_id = response.json()["cart_id"]

        # Step 2: Time passes - cart becomes abandoned (35 minutes)
        with freezegun.freeze_time("2025-01-01 12:35:00"):
            # Process abandoned carts
            with patch('tasks.cart_recovery.schedule_recovery_sequence.delay') as mock_schedule:
                result = process_abandoned_carts()

                assert result["carts_processed"] >= 1
                assert mock_schedule.called

                # Verify cart is marked as abandoned
                cart = db_session.query(AbandonedCart).filter_by(cart_id=cart_id).first()
                assert cart.status == "abandoned"
                assert cart.abandoned_at is not None

        # Step 3: Schedule recovery sequence
        with freezegun.freeze_time("2025-01-01 12:35:01"):
            mock_send_email_task.reset_mock()
            result = schedule_recovery_sequence(cart_id)

            assert result["success"] is True
            assert len(result["emails_scheduled"]) == 3

            # Verify emails were scheduled at correct times
            assert mock_send_email_task.call_count == 3

        # Step 4: Send first email (reminder)
        with freezegun.freeze_time("2025-01-01 12:35:02"):
            mock_email_service.return_value = None

            result = send_recovery_email(cart_id, "reminder")

            assert result["success"] is True
            assert mock_email_service.called

            # Verify email record was created
            email_record = db_session.query(CartRecoveryEmail).filter_by(
                cart_id=cart.id,
                email_type="reminder"
            ).first()

            assert email_record is not None
            assert email_record.status == "sent"

        # Step 5: Customer clicks recovery link
        with freezegun.freeze_time("2025-01-01 12:40:00"):
            response = client.get(f"/api/cart/recover/{cart_id}")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "recovered"
            assert data["cart_url"] is not None

        # Step 6: Verify cart is recovered in database
        db_session.refresh(cart)
        assert cart.status == "recovered"
        assert cart.recovered_at is not None

        # Step 7: Check analytics
        with freezegun.freeze_time("2025-01-01 13:00:00"):
            response = client.get("/api/cart/analytics?days=1")

            assert response.status_code == 200
            analytics = response.json()

            assert analytics["total_carts"] >= 1
            assert analytics["abandoned_carts"] >= 1
            assert analytics["recovered_carts"] >= 1
            assert analytics["recovery_rate"] > 0
            assert analytics["total_recovered_value"] == 99.99

            # Check email stats
            email_stats = analytics["email_stats"]
            assert email_stats["total_sent"] >= 1
            assert email_stats["total_opened"] == 0  # Not opened in this test
            assert email_stats["total_clicked"] == 0  # Not clicked in this test


class TestEmailService:
    """Test suite for EmailService"""

    @pytest.fixture
    def email_service(self):
        """Create EmailService instance"""
        return EmailService()

    @patch('sendgrid.SendGridAPIClient.send')
    @patch.dict('os.environ', {'SENDGRID_API_KEY': 'test_api_key', 'FROM_EMAIL': 'test@example.com'})
    def test_send_cart_recovery_email_reminder(self, mock_send, email_service):
        """Test sending reminder recovery email"""
        mock_send.return_value = Mock(status_code=202)

        context = {
            "customer_name": "John",
            "cart_items": [
                {
                    "name": "Product 1",
                    "price": 50.00,
                    "quantity": 1,
                    "subtotal": 50.00
                }
            ],
            "total_value": 50.00,
            "currency": "USD",
            "recovery_link": "https://example.com/cart/recover/123"
        }

        # Should not raise exception
        email_service.send_cart_recovery_email(
            to_email="test@example.com",
            email_type=EmailService.EMAIL_TYPE_REMINDER,
            context=context
        )

        assert mock_send.called

    @patch('sendgrid.SendGridAPIClient.send')
    @patch.dict('os.environ', {'SENDGRID_API_KEY': 'test_api_key', 'FROM_EMAIL': 'test@example.com'})
    def test_send_cart_recovery_email_sendgrid_error(self, mock_send, email_service):
        """Test email send failure handling"""
        from sendgrid.helpers.mail import Mail

        # Mock SendGrid error
        mock_send.side_effect = Exception("SendGrid API error")

        context = {
            "customer_name": "John",
            "cart_items": [],
            "total_value": 0,
            "recovery_link": "https://example.com/cart/recover/123"
        }

        # Should raise EmailServiceError
        with pytest.raises(EmailServiceError):
            email_service.send_cart_recovery_email(
                to_email="test@example.com",
                email_type=EmailService.EMAIL_TYPE_REMINDER,
                context=context
            )
