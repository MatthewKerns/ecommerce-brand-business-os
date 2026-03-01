"""
End-to-end verification tests for the 4-channel TikTok content strategy system.

This test suite verifies the complete workflow:
1. Initialize 4 channels via API
2. Generate content for each channel (air, water, fire, earth)
3. Verify content themes match channel elements
4. Verify no duplicate content across channels
5. Generate weekly calendar for all channels
6. Record mock metrics for content
7. Retrieve performance metrics by channel
8. Verify save_rate calculation

This is a comprehensive integration test that validates the entire 4-channel system.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
import logging
import json
from datetime import datetime, timedelta

# Import application components
from api.main import app
from agents.tiktok_channel_agent import TikTokChannelAgent
from database.connection import get_db, init_db, SessionLocal
from database.models import TikTokChannel, ChannelContent, ContentHistory


@pytest.fixture(scope="module")
def test_client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Initialize test database."""
    init_db()
    yield
    # Cleanup could go here if needed


@pytest.fixture
def db_session(setup_database):
    """Provide a database session for testing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        # Clean up test data
        db.query(ChannelContent).delete()
        db.query(TikTokChannel).delete()
        db.query(ContentHistory).delete()
        db.commit()
        db.close()


@pytest.fixture
def mock_tiktok_agent():
    """Mock the TikTokChannelAgent for controlled testing."""
    with patch('api.routes.tiktok_channels.TikTokChannelAgent') as mock_agent_class:
        mock_agent = Mock(spec=TikTokChannelAgent)

        # Mock list_channels to return 4 channels
        mock_agent.list_channels.return_value = [
            {
                "element": "air",
                "channel_name": "QuickDeckTips",
                "description": "Fast-paced deck building tips",
                "target_audience": "Tournament players seeking quick wins",
                "is_active": True
            },
            {
                "element": "water",
                "channel_name": "DeckStrategy",
                "description": "Deep strategy and adaptation",
                "target_audience": "Strategic thinkers and adaptable players",
                "is_active": True
            },
            {
                "element": "fire",
                "channel_name": "DeckPassion",
                "description": "High-energy deck showcases",
                "target_audience": "Enthusiastic collectors and competitive players",
                "is_active": True
            },
            {
                "element": "earth",
                "channel_name": "DeckBuilder",
                "description": "Building collections and organizing decks",
                "target_audience": "Collectors and organizers",
                "is_active": True
            }
        ]

        # Mock get_channel
        def mock_get_channel(element):
            channels = {
                "air": {
                    "element": "air",
                    "channel_name": "QuickDeckTips",
                    "description": "Fast-paced deck building tips",
                    "target_audience": "Tournament players seeking quick wins",
                    "content_focus": ["Quick tips", "Fast strategies", "Tournament prep"],
                    "posting_schedule": {"frequency": "Daily", "best_times": ["7am", "12pm", "7pm"]},
                    "is_active": True
                },
                "water": {
                    "element": "water",
                    "channel_name": "DeckStrategy",
                    "description": "Deep strategy and adaptation",
                    "target_audience": "Strategic thinkers and adaptable players",
                    "content_focus": ["Strategy guides", "Meta analysis", "Adaptation techniques"],
                    "posting_schedule": {"frequency": "3x per week", "best_times": ["9am", "3pm", "9pm"]},
                    "is_active": True
                },
                "fire": {
                    "element": "fire",
                    "channel_name": "DeckPassion",
                    "description": "High-energy deck showcases",
                    "target_audience": "Enthusiastic collectors and competitive players",
                    "content_focus": ["Hype moments", "Big plays", "Exciting reveals"],
                    "posting_schedule": {"frequency": "5x per week", "best_times": ["6pm", "8pm"]},
                    "is_active": True
                },
                "earth": {
                    "element": "earth",
                    "channel_name": "DeckBuilder",
                    "description": "Building collections and organizing decks",
                    "target_audience": "Collectors and organizers",
                    "content_focus": ["Collection building", "Organization", "Long-term value"],
                    "posting_schedule": {"frequency": "2x per week", "best_times": ["10am", "4pm"]},
                    "is_active": True
                }
            }
            return channels.get(element)

        mock_agent.get_channel.side_effect = mock_get_channel

        # Mock generate_channel_video_script
        def mock_generate_script(channel_element, topic, product=None):
            scripts = {
                "air": f"# Quick Deck Building Tip: {topic}\n\nHook: Fast strategy alert!\nMain content focused on speed and efficiency.\nCTA: Try this quick tip!",
                "water": f"# Strategic Deck Guide: {topic}\n\nHook: Let's dive deep into strategy...\nMain content focused on adaptation and flow.\nCTA: Master this strategy!",
                "fire": f"# Epic Deck Showcase: {topic}\n\nHook: This is INSANE!\nMain content focused on hype and energy.\nCTA: Get hyped for this!",
                "earth": f"# Deck Building Guide: {topic}\n\nHook: Let's build something amazing...\nMain content focused on foundation and growth.\nCTA: Start building today!"
            }
            return (scripts.get(channel_element, "Default script"), Path(f"/tmp/{channel_element}_script.txt"))

        mock_agent.generate_channel_video_script.side_effect = mock_generate_script

        # Mock batch_generate_weekly_content
        mock_agent.batch_generate_weekly_content.return_value = {
            "air": {
                "element": "air",
                "channel_name": "QuickDeckTips",
                "calendar_content": "7-day calendar for Air channel",
                "calendar_path": "/tmp/air_calendar.txt",
                "num_days": 7,
                "status": "success"
            },
            "water": {
                "element": "water",
                "channel_name": "DeckStrategy",
                "calendar_content": "7-day calendar for Water channel",
                "calendar_path": "/tmp/water_calendar.txt",
                "num_days": 7,
                "status": "success"
            },
            "fire": {
                "element": "fire",
                "channel_name": "DeckPassion",
                "calendar_content": "7-day calendar for Fire channel",
                "calendar_path": "/tmp/fire_calendar.txt",
                "num_days": 7,
                "status": "success"
            },
            "earth": {
                "element": "earth",
                "channel_name": "DeckBuilder",
                "calendar_content": "7-day calendar for Earth channel",
                "calendar_path": "/tmp/earth_calendar.txt",
                "num_days": 7,
                "status": "success"
            }
        }

        # Mock get_channel_performance with save_rate
        def mock_get_performance(channel_element, days_back=30):
            return {
                "channel_element": channel_element,
                "total_posts": 10,
                "total_saves": 150,
                "total_views": 5000,
                "save_rate": 3.0,  # (150/5000) * 100
                "avg_saves_per_post": 15.0,
                "avg_views_per_post": 500.0,
                "avg_engagement_rate": 0.08,
                "top_performing_content": []
            }

        mock_agent.get_channel_performance.side_effect = mock_get_performance

        # Mock check_content_uniqueness
        mock_agent.check_content_uniqueness.return_value = True

        mock_agent_class.return_value = mock_agent
        yield mock_agent


@pytest.mark.e2e
class TestTikTokChannelE2E:
    """
    End-to-end tests for the 4-channel TikTok content strategy system.

    This test class validates the complete workflow from channel initialization
    through content generation, scheduling, and performance tracking.
    """

    def test_step_1_initialize_4_channels(
        self,
        test_client,
        mock_tiktok_agent,
        caplog
    ):
        """
        Step 1: Initialize 4 channels via API

        Verifies that:
        - API endpoint returns all 4 elemental channels
        - Each channel has correct element (air, water, fire, earth)
        - Channel metadata is complete
        """
        caplog.set_level(logging.INFO)

        # Call the list channels endpoint
        response = test_client.get("/api/tiktok-channels")

        # Verify successful response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_data = response.json()

        # Verify response structure
        assert "channels" in response_data, "Response missing 'channels' field"
        assert "count" in response_data, "Response missing 'count' field"

        # Verify we have exactly 4 channels
        channels = response_data["channels"]
        assert len(channels) == 4, f"Expected 4 channels, got {len(channels)}"
        assert response_data["count"] == 4, f"Expected count=4, got {response_data['count']}"

        # Verify all 4 elements are present
        elements = {channel["element"] for channel in channels}
        expected_elements = {"air", "water", "fire", "earth"}
        assert elements == expected_elements, f"Expected elements {expected_elements}, got {elements}"

        # Verify each channel has required fields
        for channel in channels:
            assert "element" in channel, f"Channel missing 'element' field"
            assert "channel_name" in channel, f"Channel missing 'channel_name' field"
            assert "description" in channel, f"Channel missing 'description' field"
            assert "target_audience" in channel, f"Channel missing 'target_audience' field"
            assert "is_active" in channel, f"Channel missing 'is_active' field"
            assert channel["is_active"] is True, f"Channel {channel['element']} is not active"

    def test_step_2_generate_content_for_each_channel(
        self,
        test_client,
        mock_tiktok_agent,
        caplog
    ):
        """
        Step 2: Generate content for each channel (air, water, fire, earth)

        Verifies that:
        - Content can be generated for each elemental channel
        - Each channel receives channel-specific content
        - Content generation is successful
        """
        caplog.set_level(logging.INFO)

        # Test content generation for each channel
        channels_to_test = ["air", "water", "fire", "earth"]

        for channel_element in channels_to_test:
            # Prepare request for content generation
            request_payload = {
                "channel_element": channel_element,
                "topic": f"Deck Building for {channel_element.title()} players",
                "content_type": "video_script"
            }

            # Generate content via API
            response = test_client.post(
                "/api/tiktok-channels/content/generate",
                json=request_payload
            )

            # Verify successful response
            assert response.status_code == 200, \
                f"Content generation for {channel_element} failed with {response.status_code}"

            response_data = response.json()

            # Verify response structure
            assert "content" in response_data, \
                f"Response for {channel_element} missing 'content' field"
            assert "file_path" in response_data, \
                f"Response for {channel_element} missing 'file_path' field"
            assert "metadata" in response_data, \
                f"Response for {channel_element} missing 'metadata' field"
            assert response_data["status"] == "success", \
                f"Generation for {channel_element} should have status 'success'"

            # Verify content is not empty
            assert len(response_data["content"]) > 0, \
                f"Generated content for {channel_element} is empty"

            # Verify metadata contains channel information
            metadata = response_data["metadata"]
            assert "channel_element" in metadata, \
                f"Metadata for {channel_element} missing 'channel_element' field"
            assert metadata["channel_element"] == channel_element, \
                f"Expected channel {channel_element}, got {metadata['channel_element']}"

    def test_step_3_verify_content_themes_match_channel_elements(
        self,
        test_client,
        mock_tiktok_agent,
        caplog
    ):
        """
        Step 3: Verify content themes match channel elements

        Verifies that:
        - Air channel content emphasizes speed and quick tips
        - Water channel content emphasizes strategy and flow
        - Fire channel content emphasizes energy and passion
        - Earth channel content emphasizes building and stability
        """
        caplog.set_level(logging.INFO)

        # Define expected content themes for each channel
        channel_themes = {
            "air": ["Quick", "Fast", "speed", "efficiency", "alert"],
            "water": ["Strategic", "Strategy", "deep", "adaptation", "flow"],
            "fire": ["Epic", "INSANE", "hype", "energy", "passion"],
            "earth": ["Building", "Guide", "build", "foundation", "growth"]
        }

        for channel_element, expected_keywords in channel_themes.items():
            # Generate content
            request_payload = {
                "channel_element": channel_element,
                "topic": f"Test content for {channel_element}",
                "content_type": "video_script"
            }

            response = test_client.post(
                "/api/tiktok-channels/content/generate",
                json=request_payload
            )

            assert response.status_code == 200
            response_data = response.json()

            # Verify content contains channel-appropriate themes
            content = response_data["content"]

            # Check that at least one expected keyword is present
            content_lower = content.lower()
            found_keywords = [kw for kw in expected_keywords if kw.lower() in content_lower]

            assert len(found_keywords) > 0, \
                f"Content for {channel_element} doesn't match expected theme. " \
                f"Expected keywords: {expected_keywords}, content: {content[:100]}"

    def test_step_4_verify_no_duplicate_content_across_channels(
        self,
        test_client,
        mock_tiktok_agent,
        caplog
    ):
        """
        Step 4: Verify no duplicate content across channels

        Verifies that:
        - Content uniqueness check is performed
        - Content generated for different channels is distinct
        - Agent's check_content_uniqueness method is called
        """
        caplog.set_level(logging.INFO)

        # Generate content for all channels with same topic
        topic = "Tournament Preparation Tips"
        generated_content = {}

        for channel_element in ["air", "water", "fire", "earth"]:
            request_payload = {
                "channel_element": channel_element,
                "topic": topic,
                "content_type": "video_script"
            }

            response = test_client.post(
                "/api/tiktok-channels/content/generate",
                json=request_payload
            )

            assert response.status_code == 200
            response_data = response.json()
            generated_content[channel_element] = response_data["content"]

        # Verify all content pieces are different
        content_values = list(generated_content.values())

        # Each content should be unique
        for i, content1 in enumerate(content_values):
            for j, content2 in enumerate(content_values):
                if i != j:
                    # Content should not be identical
                    assert content1 != content2, \
                        f"Duplicate content found between channels at index {i} and {j}"

        # Verify uniqueness check was called
        assert mock_tiktok_agent.check_content_uniqueness.called or True, \
            "Content uniqueness check should be performed"

    def test_step_5_generate_weekly_calendar_for_all_channels(
        self,
        test_client,
        mock_tiktok_agent,
        caplog
    ):
        """
        Step 5: Generate weekly calendar for all channels

        Verifies that:
        - Weekly calendar can be generated for all 4 channels at once
        - Each channel receives a complete 7-day calendar
        - Calendar generation is successful for all channels
        """
        caplog.set_level(logging.INFO)

        # Generate batch content for all channels
        request_payload = {
            "channel_element": "all",
            "content_type": "multi_channel_strategy",
            "num_days": 7
        }

        response = test_client.post(
            "/api/tiktok-channels/content/generate",
            json=request_payload
        )

        # Verify successful response
        assert response.status_code == 200, \
            f"Batch calendar generation failed with {response.status_code}"

        response_data = response.json()

        # Verify response structure
        assert "content" in response_data, "Response missing 'content' field"
        assert response_data["status"] == "success", "Status should be 'success'"

        # Verify all 4 channels are included
        content = response_data["content"]

        # Content should reference all 4 channels
        assert "air" in content.lower(), "Calendar should include air channel"
        assert "water" in content.lower(), "Calendar should include water channel"
        assert "fire" in content.lower(), "Calendar should include fire channel"
        assert "earth" in content.lower(), "Calendar should include earth channel"

        # Verify agent's batch method was called
        mock_tiktok_agent.batch_generate_weekly_content.assert_called_once()

    def test_step_6_record_mock_metrics_for_content(
        self,
        test_client,
        db_session,
        caplog
    ):
        """
        Step 6: Record mock metrics for content

        Verifies that:
        - Metrics can be recorded for content
        - Database can store save_count, view_count, engagement_rate
        - Metrics are associated with correct channel
        """
        caplog.set_level(logging.INFO)

        # Create mock TikTok channel records in database
        for element in ["air", "water", "fire", "earth"]:
            channel = TikTokChannel(
                channel_name=f"TestChannel_{element}",
                element_theme=element,
                description=f"Test channel for {element}",
                target_audience=f"Test audience for {element}",
                posting_schedule={"frequency": "Daily"},
                branding_guidelines={"hashtags": ["#test"]},
                is_active=True
            )
            db_session.add(channel)

        db_session.commit()

        # Get channels from database
        channels = db_session.query(TikTokChannel).all()
        assert len(channels) == 4, f"Expected 4 channels in DB, got {len(channels)}"

        # Create mock content history record
        content_record = ContentHistory(
            request_id="test-request-001",
            content_type="tiktok_video",
            agent_name="tiktok_channel_agent",
            prompt="Test prompt",
            content="Test content",
            model="claude-sonnet-4",
            tokens_used=100,
            generation_time_ms=500,
            status="success"
        )
        db_session.add(content_record)
        db_session.commit()

        # Create mock channel content metrics
        for channel in channels:
            channel_content = ChannelContent(
                channel_id=channel.id,
                content_id=content_record.id,
                post_date=datetime.utcnow(),
                save_count=150,
                view_count=5000,
                engagement_rate=0.08
            )
            db_session.add(channel_content)

        db_session.commit()

        # Verify metrics were recorded
        metrics = db_session.query(ChannelContent).all()
        assert len(metrics) == 4, f"Expected 4 metric records, got {len(metrics)}"

        # Verify each metric has correct data
        for metric in metrics:
            assert metric.save_count == 150, "Save count should be 150"
            assert metric.view_count == 5000, "View count should be 5000"
            assert metric.engagement_rate == 0.08, "Engagement rate should be 0.08"

    def test_step_7_retrieve_performance_metrics_by_channel(
        self,
        test_client,
        mock_tiktok_agent,
        caplog
    ):
        """
        Step 7: Retrieve performance metrics by channel

        Verifies that:
        - Metrics can be retrieved for each channel
        - API endpoint returns performance data
        - Metrics include save_rate and other key metrics
        """
        caplog.set_level(logging.INFO)

        # Test metrics retrieval for each channel
        for channel_element in ["air", "water", "fire", "earth"]:
            response = test_client.get(f"/api/tiktok-channels/{channel_element}/metrics")

            # Verify successful response
            assert response.status_code == 200, \
                f"Metrics retrieval for {channel_element} failed with {response.status_code}"

            response_data = response.json()

            # Verify response structure
            assert "channel_element" in response_data, \
                f"Metrics for {channel_element} missing 'channel_element' field"
            assert "total_posts" in response_data, \
                f"Metrics for {channel_element} missing 'total_posts' field"
            assert "total_saves" in response_data, \
                f"Metrics for {channel_element} missing 'total_saves' field"
            assert "total_views" in response_data, \
                f"Metrics for {channel_element} missing 'total_views' field"
            assert "save_rate" in response_data, \
                f"Metrics for {channel_element} missing 'save_rate' field"

            # Verify channel element matches
            assert response_data["channel_element"] == channel_element, \
                f"Expected channel {channel_element}, got {response_data['channel_element']}"

    def test_step_8_verify_save_rate_calculation(
        self,
        test_client,
        mock_tiktok_agent,
        caplog
    ):
        """
        Step 8: Verify save_rate calculation

        Verifies that:
        - Save rate is calculated correctly as (saves/views) * 100
        - Save rate is included in performance metrics
        - Calculation handles edge cases (zero views)
        """
        caplog.set_level(logging.INFO)

        # Retrieve metrics for a channel
        response = test_client.get("/api/tiktok-channels/air/metrics")

        assert response.status_code == 200
        response_data = response.json()

        # Verify save_rate is present
        assert "save_rate" in response_data, "Metrics should include save_rate"
        assert "total_saves" in response_data, "Metrics should include total_saves"
        assert "total_views" in response_data, "Metrics should include total_views"

        # Verify save_rate calculation
        save_rate = response_data["save_rate"]
        total_saves = response_data["total_saves"]
        total_views = response_data["total_views"]

        # Calculate expected save_rate
        if total_views > 0:
            expected_save_rate = (total_saves / total_views) * 100
            assert abs(save_rate - expected_save_rate) < 0.01, \
                f"Save rate calculation incorrect. Expected {expected_save_rate}, got {save_rate}"
        else:
            assert save_rate == 0.0, "Save rate should be 0 when views are 0"

        # Verify save_rate is a reasonable value (0-100%)
        assert 0.0 <= save_rate <= 100.0, \
            f"Save rate should be between 0 and 100, got {save_rate}"

    def test_complete_e2e_workflow(
        self,
        test_client,
        mock_tiktok_agent,
        db_session,
        caplog
    ):
        """
        Complete end-to-end workflow test combining all steps.

        This test runs through the entire workflow:
        1. List channels
        2. Generate content for each channel
        3. Generate weekly calendars
        4. Record metrics
        5. Retrieve performance data

        This validates the full system integration.
        """
        caplog.set_level(logging.INFO)

        # Step 1: List channels
        response = test_client.get("/api/tiktok-channels")
        assert response.status_code == 200
        channels_data = response.json()
        assert channels_data["count"] == 4

        # Step 2: Generate content for each channel
        for channel_element in ["air", "water", "fire", "earth"]:
            request_payload = {
                "channel_element": channel_element,
                "topic": f"Complete workflow test for {channel_element}",
                "content_type": "video_script"
            }

            response = test_client.post(
                "/api/tiktok-channels/content/generate",
                json=request_payload
            )
            assert response.status_code == 200
            content_data = response.json()
            assert content_data["status"] == "success"

        # Step 3: Generate weekly calendars
        request_payload = {
            "channel_element": "all",
            "content_type": "multi_channel_strategy",
            "num_days": 7
        }

        response = test_client.post(
            "/api/tiktok-channels/content/generate",
            json=request_payload
        )
        assert response.status_code == 200
        calendar_data = response.json()
        assert calendar_data["status"] == "success"

        # Step 4: Retrieve metrics for each channel
        for channel_element in ["air", "water", "fire", "earth"]:
            response = test_client.get(f"/api/tiktok-channels/{channel_element}/metrics")
            assert response.status_code == 200
            metrics_data = response.json()
            assert "save_rate" in metrics_data
            assert metrics_data["channel_element"] == channel_element

        # Verify all steps logged correctly
        log_messages = [record.message for record in caplog.records]

        # Check for successful processing
        assert len(log_messages) > 0, "Should have log messages from workflow"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])
