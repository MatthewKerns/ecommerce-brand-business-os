"""
TikTok Shop API Client

This module provides the main API client for interacting with TikTok Shop APIs,
including Shop API, Content API, and Data API endpoints.
"""
import time
import requests
from typing import Dict, Optional, Any
from urllib.parse import urljoin

from config.config import TIKTOK_SHOP_API_BASE_URL
from integrations.tiktok_shop.oauth import TikTokShopOAuth
from integrations.tiktok_shop.exceptions import (
    TikTokShopAPIError,
    TikTokShopAuthError,
    TikTokShopRateLimitError,
    TikTokShopValidationError,
    TikTokShopNotFoundError,
    TikTokShopServerError,
    TikTokShopNetworkError
)


class TikTokShopClient:
    """
    Main client for TikTok Shop API integration

    This client provides methods for interacting with TikTok Shop's various APIs:
    - Shop API: Products, orders, inventory management
    - Content API: Video and post management
    - Data API: Analytics and performance metrics

    Attributes:
        app_key: TikTok Shop application key
        app_secret: TikTok Shop application secret
        access_token: Access token for authenticated requests
        api_base_url: Base URL for TikTok Shop API
        oauth: OAuth handler for authentication
    """

    # Default request timeout in seconds
    DEFAULT_TIMEOUT = 30

    # API version
    API_VERSION = "202309"

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        access_token: Optional[str] = None,
        api_base_url: str = TIKTOK_SHOP_API_BASE_URL
    ):
        """
        Initialize TikTok Shop API client

        Args:
            app_key: TikTok Shop application key
            app_secret: TikTok Shop application secret
            access_token: Access token for API requests (optional, can be set later)
            api_base_url: Base URL for TikTok Shop API

        Raises:
            TikTokShopAuthError: If required credentials are missing

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> # Client is ready to make API requests
        """
        if not app_key or not app_secret:
            raise TikTokShopAuthError(
                "Missing required credentials: app_key and app_secret are required"
            )

        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.api_base_url = api_base_url.rstrip('/')

        # Initialize OAuth handler for authentication
        self.oauth = TikTokShopOAuth(app_key, app_secret, api_base_url)

    def set_access_token(self, access_token: str) -> None:
        """
        Set or update the access token

        Args:
            access_token: New access token to use for API requests

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret')
            >>> client.set_access_token('new_access_token')
        """
        self.access_token = access_token

    def _build_common_params(self) -> Dict[str, Any]:
        """
        Build common parameters required for all API requests

        Returns:
            Dictionary containing common parameters like app_key, timestamp, etc.
        """
        timestamp = int(time.time())

        return {
            'app_key': self.app_key,
            'timestamp': timestamp
        }

    def _generate_request_signature(
        self,
        path: str,
        params: Dict[str, Any]
    ) -> str:
        """
        Generate signature for API request

        Args:
            path: API endpoint path
            params: Request parameters

        Returns:
            Generated signature string
        """
        return self.oauth.generate_signature(path, params)

    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to TikTok Shop API

        This is the core request method that handles:
        - Adding common parameters
        - Generating signatures
        - Adding authentication headers
        - Making the HTTP request
        - Parsing and validating the response
        - Error handling

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path (e.g., '/api/products/search')
            params: Query parameters for GET requests
            data: Body data for POST/PUT requests
            require_auth: Whether this request requires authentication
            timeout: Request timeout in seconds (uses DEFAULT_TIMEOUT if not provided)

        Returns:
            Parsed JSON response from the API

        Raises:
            TikTokShopAuthError: For authentication errors
            TikTokShopRateLimitError: For rate limit errors
            TikTokShopValidationError: For validation errors
            TikTokShopNotFoundError: For 404 errors
            TikTokShopServerError: For server errors
            TikTokShopNetworkError: For network errors
            TikTokShopAPIError: For other API errors

        Example:
            >>> response = client._make_request('GET', '/api/products/search',
            ...                                  params={'page_size': 10})
        """
        if require_auth and not self.access_token:
            raise TikTokShopAuthError(
                "Access token is required for this request. "
                "Set it using set_access_token() or during initialization."
            )

        # Build the full URL
        url = urljoin(self.api_base_url, path)

        # Initialize parameters
        if params is None:
            params = {}

        # Add common parameters
        common_params = self._build_common_params()
        params.update(common_params)

        # Add access token if authentication is required
        if require_auth:
            params['access_token'] = self.access_token

        # Generate signature
        signature = self._generate_request_signature(path, params)
        params['sign'] = signature

        # Set timeout
        request_timeout = timeout or self.DEFAULT_TIMEOUT

        # Make the request
        try:
            if method.upper() in ['GET', 'DELETE']:
                response = requests.request(
                    method,
                    url,
                    params=params,
                    timeout=request_timeout
                )
            else:  # POST, PUT
                response = requests.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    timeout=request_timeout
                )

            # Handle HTTP errors
            response.raise_for_status()

            # Parse JSON response
            response_data = response.json()

            # Check for API-level errors
            return self._handle_api_response(response_data)

        except requests.exceptions.Timeout as e:
            raise TikTokShopNetworkError(
                f"Request timeout after {request_timeout}s",
                original_exception=e
            )
        except requests.exceptions.ConnectionError as e:
            raise TikTokShopNetworkError(
                "Failed to connect to TikTok Shop API",
                original_exception=e
            )
        except requests.exceptions.HTTPError as e:
            self._handle_http_error(e, response)
        except requests.exceptions.RequestException as e:
            raise TikTokShopNetworkError(
                f"Network error during API request: {str(e)}",
                original_exception=e
            )
        except ValueError as e:
            raise TikTokShopAPIError(
                "Failed to parse JSON response from API"
            )
        except Exception as e:
            raise TikTokShopAPIError(
                f"Unexpected error during API request: {str(e)}"
            )

    def _handle_api_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle and validate API response

        Args:
            response_data: Parsed JSON response from API

        Returns:
            Response data if successful

        Raises:
            TikTokShopAPIError: If API returns an error code
        """
        # TikTok Shop API uses 'code' field to indicate success/failure
        # code = 0 means success
        code = response_data.get('code', -1)

        if code != 0:
            message = response_data.get('message', 'Unknown API error')

            # Map common error codes to specific exceptions
            if code in [401, 10002, 10003]:  # Auth-related errors
                raise TikTokShopAuthError(
                    f"Authentication error: {message}",
                    status_code=code,
                    response=response_data
                )
            elif code == 429 or code == 10001:  # Rate limit
                retry_after = response_data.get('retry_after')
                raise TikTokShopRateLimitError(
                    f"Rate limit exceeded: {message}",
                    status_code=code,
                    response=response_data,
                    retry_after=retry_after
                )
            elif code in [400, 40000, 40001]:  # Validation errors
                raise TikTokShopValidationError(
                    f"Validation error: {message}",
                    status_code=code,
                    response=response_data
                )
            elif code == 404 or code == 40004:  # Not found
                raise TikTokShopNotFoundError(
                    f"Resource not found: {message}",
                    status_code=code,
                    response=response_data
                )
            elif code >= 500:  # Server errors
                raise TikTokShopServerError(
                    f"Server error: {message}",
                    status_code=code,
                    response=response_data
                )
            else:  # Generic API error
                raise TikTokShopAPIError(
                    f"API error: {message}",
                    status_code=code,
                    response=response_data
                )

        return response_data

    def _handle_http_error(
        self,
        error: requests.exceptions.HTTPError,
        response: requests.Response
    ) -> None:
        """
        Handle HTTP errors from requests

        Args:
            error: The HTTP error exception
            response: The response object

        Raises:
            Appropriate TikTokShop exception based on status code
        """
        status_code = response.status_code

        try:
            response_data = response.json()
            message = response_data.get('message', str(error))
        except:
            response_data = None
            message = str(error)

        if status_code == 401:
            raise TikTokShopAuthError(
                f"Authentication failed: {message}",
                status_code=status_code,
                response=response_data
            )
        elif status_code == 429:
            retry_after = response.headers.get('Retry-After')
            raise TikTokShopRateLimitError(
                f"Rate limit exceeded: {message}",
                status_code=status_code,
                response=response_data,
                retry_after=int(retry_after) if retry_after else None
            )
        elif status_code == 400:
            raise TikTokShopValidationError(
                f"Invalid request: {message}",
                status_code=status_code,
                response=response_data
            )
        elif status_code == 404:
            raise TikTokShopNotFoundError(
                f"Resource not found: {message}",
                status_code=status_code,
                response=response_data
            )
        elif status_code >= 500:
            raise TikTokShopServerError(
                f"Server error: {message}",
                status_code=status_code,
                response=response_data
            )
        else:
            raise TikTokShopAPIError(
                f"HTTP error {status_code}: {message}",
                status_code=status_code,
                response=response_data
            )

    # ========================================================================
    # SHOP API METHODS - Products, Orders, Inventory
    # ========================================================================

    def get_products(
        self,
        page_size: int = 20,
        page_number: int = 1,
        status: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get list of products from TikTok Shop

        Args:
            page_size: Number of products per page (max 100)
            page_number: Page number to retrieve (starts at 1)
            status: Filter by product status ('ACTIVE', 'INACTIVE', 'DRAFT')
            search_query: Optional search query to filter products

        Returns:
            Dictionary containing:
                - products: List of product objects
                - total: Total number of products
                - more: Boolean indicating if more pages exist

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopValidationError: If parameters are invalid
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> response = client.get_products(page_size=10, status='ACTIVE')
            >>> products = response['data']['products']
        """
        params = {
            'page_size': min(page_size, 100),  # Cap at 100 per API limits
            'page_number': page_number
        }

        if status:
            params['status'] = status

        if search_query:
            params['search_query'] = search_query

        return self._make_request(
            method='GET',
            path='/api/products/search',
            params=params
        )

    def get_product(self, product_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific product

        Args:
            product_id: TikTok Shop product ID

        Returns:
            Dictionary containing detailed product information

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopNotFoundError: If product not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> product = client.get_product('1234567890')
            >>> product_name = product['data']['title']
        """
        return self._make_request(
            method='GET',
            path='/api/products/details',
            params={'product_id': product_id}
        )

    def get_orders(
        self,
        page_size: int = 20,
        page_number: int = 1,
        order_status: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get list of orders from TikTok Shop

        Args:
            page_size: Number of orders per page (max 100)
            page_number: Page number to retrieve (starts at 1)
            order_status: Filter by order status ('UNPAID', 'AWAITING_SHIPMENT',
                         'AWAITING_COLLECTION', 'IN_TRANSIT', 'DELIVERED', 'COMPLETED', 'CANCELLED')
            start_time: Start timestamp for order creation time (Unix timestamp)
            end_time: End timestamp for order creation time (Unix timestamp)

        Returns:
            Dictionary containing:
                - orders: List of order objects
                - total: Total number of orders
                - more: Boolean indicating if more pages exist

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopValidationError: If parameters are invalid
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> response = client.get_orders(page_size=10, order_status='AWAITING_SHIPMENT')
            >>> orders = response['data']['orders']
        """
        params = {
            'page_size': min(page_size, 100),  # Cap at 100 per API limits
            'page_number': page_number
        }

        if order_status:
            params['order_status'] = order_status

        if start_time:
            params['start_time'] = start_time

        if end_time:
            params['end_time'] = end_time

        return self._make_request(
            method='GET',
            path='/api/orders/search',
            params=params
        )

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific order

        Args:
            order_id: TikTok Shop order ID

        Returns:
            Dictionary containing detailed order information

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopNotFoundError: If order not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> order = client.get_order('ORDER123456')
            >>> order_total = order['data']['payment']['total_amount']
        """
        return self._make_request(
            method='GET',
            path='/api/orders/detail',
            params={'order_id': order_id}
        )

    def update_inventory(
        self,
        product_id: str,
        quantity: int,
        sku_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update inventory quantity for a product or specific SKU

        Args:
            product_id: TikTok Shop product ID
            quantity: New inventory quantity (must be >= 0)
            sku_id: Optional SKU ID if updating specific variant

        Returns:
            Dictionary containing updated inventory information

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopValidationError: If parameters are invalid (e.g., negative quantity)
            TikTokShopNotFoundError: If product or SKU not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> result = client.update_inventory('1234567890', quantity=100)
            >>> new_quantity = result['data']['available_quantity']
        """
        if quantity < 0:
            raise TikTokShopValidationError(
                "Inventory quantity must be non-negative",
                status_code=400
            )

        data = {
            'product_id': product_id,
            'available_quantity': quantity
        }

        if sku_id:
            data['sku_id'] = sku_id

        return self._make_request(
            method='POST',
            path='/api/products/inventory/update',
            data=data
        )

    def get_inventory(self, product_id: str) -> Dict[str, Any]:
        """
        Get current inventory information for a product

        Args:
            product_id: TikTok Shop product ID

        Returns:
            Dictionary containing inventory information including:
                - available_quantity: Current available inventory
                - reserved_quantity: Quantity reserved for orders
                - sku_inventory: Inventory breakdown by SKU (if applicable)

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopNotFoundError: If product not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> inventory = client.get_inventory('1234567890')
            >>> available = inventory['data']['available_quantity']
        """
        return self._make_request(
            method='GET',
            path='/api/products/inventory',
            params={'product_id': product_id}
        )

    # ========================================================================
    # CONTENT API METHODS - Videos, Posts
    # ========================================================================

    def get_videos(
        self,
        page_size: int = 20,
        page_number: int = 1,
        video_status: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get list of videos from TikTok Shop

        Args:
            page_size: Number of videos per page (max 100)
            page_number: Page number to retrieve (starts at 1)
            video_status: Filter by video status ('PUBLISHED', 'DRAFT', 'PROCESSING', 'FAILED')
            start_time: Start timestamp for video creation time (Unix timestamp)
            end_time: End timestamp for video creation time (Unix timestamp)

        Returns:
            Dictionary containing:
                - videos: List of video objects
                - total: Total number of videos
                - more: Boolean indicating if more pages exist

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopValidationError: If parameters are invalid
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> response = client.get_videos(page_size=10, video_status='PUBLISHED')
            >>> videos = response['data']['videos']
        """
        params = {
            'page_size': min(page_size, 100),  # Cap at 100 per API limits
            'page_number': page_number
        }

        if video_status:
            params['video_status'] = video_status

        if start_time:
            params['start_time'] = start_time

        if end_time:
            params['end_time'] = end_time

        return self._make_request(
            method='GET',
            path='/api/content/videos',
            params=params
        )

    def get_video(self, video_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific video

        Args:
            video_id: TikTok Shop video ID

        Returns:
            Dictionary containing detailed video information including:
                - video_id: Video identifier
                - title: Video title
                - description: Video description
                - status: Video status
                - url: Video URL
                - thumbnail_url: Thumbnail image URL
                - duration: Video duration in seconds
                - view_count: Number of views
                - like_count: Number of likes
                - share_count: Number of shares
                - created_time: Creation timestamp

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopNotFoundError: If video not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> video = client.get_video('VIDEO123456')
            >>> video_url = video['data']['url']
        """
        return self._make_request(
            method='GET',
            path='/api/content/video/detail',
            params={'video_id': video_id}
        )

    def upload_video(
        self,
        video_url: str,
        title: str,
        description: Optional[str] = None,
        product_ids: Optional[list] = None,
        tags: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Upload a video to TikTok Shop

        Args:
            video_url: URL of the video to upload (must be accessible)
            title: Video title (max 150 characters)
            description: Video description (max 1000 characters)
            product_ids: List of product IDs to tag in the video
            tags: List of hashtags (without # symbol)

        Returns:
            Dictionary containing:
                - video_id: ID of the uploaded video
                - status: Upload status
                - processing_time: Estimated processing time in seconds

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopValidationError: If parameters are invalid
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> result = client.upload_video(
            ...     video_url='https://example.com/video.mp4',
            ...     title='New Product Showcase',
            ...     product_ids=['1234567890']
            ... )
            >>> video_id = result['data']['video_id']
        """
        if not title or len(title) > 150:
            raise TikTokShopValidationError(
                "Video title is required and must be 150 characters or less",
                status_code=400
            )

        data = {
            'video_url': video_url,
            'title': title
        }

        if description:
            if len(description) > 1000:
                raise TikTokShopValidationError(
                    "Video description must be 1000 characters or less",
                    status_code=400
                )
            data['description'] = description

        if product_ids:
            data['product_ids'] = product_ids

        if tags:
            data['tags'] = tags

        return self._make_request(
            method='POST',
            path='/api/content/video/upload',
            data=data
        )

    def delete_video(self, video_id: str) -> Dict[str, Any]:
        """
        Delete a video from TikTok Shop

        Args:
            video_id: TikTok Shop video ID to delete

        Returns:
            Dictionary containing deletion confirmation

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopNotFoundError: If video not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> result = client.delete_video('VIDEO123456')
        """
        return self._make_request(
            method='DELETE',
            path='/api/content/video/delete',
            params={'video_id': video_id}
        )

    def get_posts(
        self,
        page_size: int = 20,
        page_number: int = 1,
        post_status: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get list of posts from TikTok Shop

        Args:
            page_size: Number of posts per page (max 100)
            page_number: Page number to retrieve (starts at 1)
            post_status: Filter by post status ('PUBLISHED', 'DRAFT', 'SCHEDULED')
            start_time: Start timestamp for post creation time (Unix timestamp)
            end_time: End timestamp for post creation time (Unix timestamp)

        Returns:
            Dictionary containing:
                - posts: List of post objects
                - total: Total number of posts
                - more: Boolean indicating if more pages exist

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopValidationError: If parameters are invalid
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> response = client.get_posts(page_size=10, post_status='PUBLISHED')
            >>> posts = response['data']['posts']
        """
        params = {
            'page_size': min(page_size, 100),  # Cap at 100 per API limits
            'page_number': page_number
        }

        if post_status:
            params['post_status'] = post_status

        if start_time:
            params['start_time'] = start_time

        if end_time:
            params['end_time'] = end_time

        return self._make_request(
            method='GET',
            path='/api/content/posts',
            params=params
        )

    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific post

        Args:
            post_id: TikTok Shop post ID

        Returns:
            Dictionary containing detailed post information including:
                - post_id: Post identifier
                - content: Post content/text
                - status: Post status
                - media: List of attached media (images/videos)
                - product_tags: Tagged products
                - engagement: Engagement metrics (likes, comments, shares)
                - created_time: Creation timestamp
                - scheduled_time: Scheduled publish time (if applicable)

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopNotFoundError: If post not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> post = client.get_post('POST123456')
            >>> content = post['data']['content']
        """
        return self._make_request(
            method='GET',
            path='/api/content/post/detail',
            params={'post_id': post_id}
        )

    def create_post(
        self,
        content: str,
        media_urls: Optional[list] = None,
        product_ids: Optional[list] = None,
        tags: Optional[list] = None,
        scheduled_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new post on TikTok Shop

        Args:
            content: Post content/text (max 2000 characters)
            media_urls: List of media URLs (images/videos) to attach
            product_ids: List of product IDs to tag in the post
            tags: List of hashtags (without # symbol)
            scheduled_time: Unix timestamp for scheduled publishing (optional)

        Returns:
            Dictionary containing:
                - post_id: ID of the created post
                - status: Post status ('PUBLISHED' or 'SCHEDULED')
                - url: Post URL

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopValidationError: If parameters are invalid
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> result = client.create_post(
            ...     content='Check out our new products!',
            ...     product_ids=['1234567890'],
            ...     tags=['newarrivals', 'shopping']
            ... )
            >>> post_id = result['data']['post_id']
        """
        if not content or len(content) > 2000:
            raise TikTokShopValidationError(
                "Post content is required and must be 2000 characters or less",
                status_code=400
            )

        data = {
            'content': content
        }

        if media_urls:
            data['media_urls'] = media_urls

        if product_ids:
            data['product_ids'] = product_ids

        if tags:
            data['tags'] = tags

        if scheduled_time:
            data['scheduled_time'] = scheduled_time

        return self._make_request(
            method='POST',
            path='/api/content/post/create',
            data=data
        )

    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """
        Delete a post from TikTok Shop

        Args:
            post_id: TikTok Shop post ID to delete

        Returns:
            Dictionary containing deletion confirmation

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopNotFoundError: If post not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> client = TikTokShopClient('app_key', 'app_secret', 'access_token')
            >>> result = client.delete_post('POST123456')
        """
        return self._make_request(
            method='DELETE',
            path='/api/content/post/delete',
            params={'post_id': post_id}
        )
