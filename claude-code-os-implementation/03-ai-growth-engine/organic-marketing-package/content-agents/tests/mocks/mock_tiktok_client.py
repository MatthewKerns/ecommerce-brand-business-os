"""
Mock TikTok Shop Client for E2E Testing

This module provides a mock implementation of the TikTokShopClient
that simulates successful API responses without making real API calls.

Usage:
    >>> from tests.mocks.mock_tiktok_client import MockTikTokShopClient
    >>> client = MockTikTokShopClient()
    >>> result = client.create_post(content="test", product_ids=[])
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class MockTikTokShopClient:
    """
    Mock TikTok Shop Client for testing purposes.

    This client simulates successful API responses for:
    - create_post(): Creates TikTok Shop posts
    - upload_video(): Uploads TikTok videos
    - get_post_status(): Gets post status

    All methods return realistic mock responses without making real API calls.
    """

    def __init__(self, *args, **kwargs):
        """Initialize mock client (accepts any arguments for compatibility)."""
        self.app_key = kwargs.get('app_key', 'mock_app_key')
        self.app_secret = kwargs.get('app_secret', 'mock_app_secret')
        self.access_token = kwargs.get('access_token', 'mock_access_token')
        self.api_base_url = kwargs.get('api_base_url', 'https://mock-api.tiktok.com')

        # Track calls for verification
        self.call_history = []

    def create_post(
        self,
        content: str,
        media_urls: Optional[List[str]] = None,
        product_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        scheduled_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mock create_post method that returns a successful response.

        Args:
            content: Post content text
            media_urls: Optional list of media URLs
            product_ids: Optional list of product IDs to tag
            tags: Optional list of hashtags
            scheduled_time: Optional scheduled publish time

        Returns:
            Dict containing mock response with post ID
        """
        # Generate mock post ID
        mock_post_id = f"mock_post_{uuid.uuid4().hex[:12]}"

        # Track call
        self.call_history.append({
            'method': 'create_post',
            'args': {
                'content': content,
                'media_urls': media_urls,
                'product_ids': product_ids,
                'tags': tags,
                'scheduled_time': scheduled_time
            },
            'timestamp': datetime.utcnow().isoformat()
        })

        # Simulate API processing time
        time.sleep(0.1)

        # Return mock successful response
        return {
            'code': 0,
            'message': 'success',
            'data': {
                'item_id': mock_post_id,
                'status': 'published',
                'share_url': f'https://tiktok.com/mock/{mock_post_id}',
                'created_at': int(time.time())
            }
        }

    def upload_video(
        self,
        video_url: str,
        title: str,
        description: Optional[str] = None,
        product_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        scheduled_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mock upload_video method that returns a successful response.

        Args:
            video_url: URL of the video to upload
            title: Video title
            description: Optional video description
            product_ids: Optional list of product IDs to tag
            tags: Optional list of hashtags
            scheduled_time: Optional scheduled publish time

        Returns:
            Dict containing mock response with video ID
        """
        # Generate mock video ID
        mock_video_id = f"mock_video_{uuid.uuid4().hex[:12]}"

        # Track call
        self.call_history.append({
            'method': 'upload_video',
            'args': {
                'video_url': video_url,
                'title': title,
                'description': description,
                'product_ids': product_ids,
                'tags': tags,
                'scheduled_time': scheduled_time
            },
            'timestamp': datetime.utcnow().isoformat()
        })

        # Simulate API processing time
        time.sleep(0.2)

        # Return mock successful response
        return {
            'code': 0,
            'message': 'success',
            'data': {
                'video_id': mock_video_id,
                'status': 'published',
                'share_url': f'https://tiktok.com/mock/{mock_video_id}',
                'created_at': int(time.time()),
                'views': 0,
                'likes': 0
            }
        }

    def get_post_status(self, post_id: str) -> Dict[str, Any]:
        """
        Mock get_post_status method that returns post status.

        Args:
            post_id: ID of the post to check

        Returns:
            Dict containing mock post status
        """
        # Track call
        self.call_history.append({
            'method': 'get_post_status',
            'args': {'post_id': post_id},
            'timestamp': datetime.utcnow().isoformat()
        })

        # Return mock status response
        return {
            'code': 0,
            'message': 'success',
            'data': {
                'item_id': post_id,
                'status': 'published',
                'views': 1234,
                'likes': 56,
                'comments': 7,
                'shares': 3
            }
        }

    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Mock get_video_status method that returns video status.

        Args:
            video_id: ID of the video to check

        Returns:
            Dict containing mock video status
        """
        # Track call
        self.call_history.append({
            'method': 'get_video_status',
            'args': {'video_id': video_id},
            'timestamp': datetime.utcnow().isoformat()
        })

        # Return mock status response
        return {
            'code': 0,
            'message': 'success',
            'data': {
                'video_id': video_id,
                'status': 'published',
                'views': 5678,
                'likes': 234,
                'comments': 45,
                'shares': 12
            }
        }

    def reset_call_history(self):
        """Reset the call history (useful for testing)."""
        self.call_history = []

    def get_call_count(self, method_name: Optional[str] = None) -> int:
        """
        Get the number of calls made.

        Args:
            method_name: Optional method name to filter by

        Returns:
            Number of calls
        """
        if method_name:
            return sum(1 for call in self.call_history if call['method'] == method_name)
        return len(self.call_history)
