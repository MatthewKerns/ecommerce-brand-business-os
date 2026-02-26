"""
TikTok Shop Integration Agent
Manages TikTok Shop content, products, orders, and analytics
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base_agent import BaseAgent
from config.config import TIKTOK_OUTPUT_DIR, TIKTOK_SHOP_APP_KEY, TIKTOK_SHOP_APP_SECRET


class TikTokShopAgent(BaseAgent):
    """Agent specialized in TikTok Shop integration and content"""

    def __init__(
        self,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        access_token: Optional[str] = None
    ):
        """
        Initialize the TikTok Shop agent

        Args:
            app_key: TikTok Shop application key (defaults to config)
            app_secret: TikTok Shop application secret (defaults to config)
            access_token: Access token for authenticated requests (optional)
        """
        super().__init__(agent_name="tiktok_shop_agent")

        # Use provided credentials or fall back to config
        self.app_key = app_key or TIKTOK_SHOP_APP_KEY
        self.app_secret = app_secret or TIKTOK_SHOP_APP_SECRET
        self.access_token = access_token

        # TikTok Shop API client will be initialized when needed
        self._client = None

        # Platform-specific parameters
        self.platform_specs = {
            "video": {
                "max_duration": 180,  # 3 minutes
                "recommended_duration": 60,  # 1 minute
                "aspect_ratio": "9:16",  # Vertical
                "tone": "Energetic, authentic, product-focused"
            },
            "post": {
                "caption_length": 2200,
                "hashtag_count": 30,
                "tone": "Direct, action-oriented, value-driven"
            },
            "live": {
                "recommended_duration": 1800,  # 30 minutes
                "tone": "Interactive, engaging, sales-focused"
            }
        }

        # Content strategy for TikTok Shop
        self.content_strategy = {
            "product_showcase": "Demonstrate product features and benefits",
            "unboxing": "Create excitement around product presentation",
            "tutorial": "Show how to use products effectively",
            "battle_ready": "Connect products to battle-ready lifestyle",
            "community": "Feature customer stories and testimonials",
            "behind_scenes": "Share brand story and product development"
        }

    def _get_client(self):
        """
        Get or create TikTok Shop API client

        Returns:
            TikTokShopClient instance

        Raises:
            ValueError: If credentials are not configured
        """
        if self._client is None:
            if not self.app_key or not self.app_secret:
                raise ValueError(
                    "TikTok Shop credentials not configured. "
                    "Set TIKTOK_SHOP_APP_KEY and TIKTOK_SHOP_APP_SECRET in .env "
                    "or pass them to TikTokShopAgent constructor."
                )

            # Import here to avoid circular dependencies
            from integrations.tiktok_shop.client import TikTokShopClient

            self._client = TikTokShopClient(
                app_key=self.app_key,
                app_secret=self.app_secret,
                access_token=self.access_token
            )

        return self._client

    def set_access_token(self, access_token: str) -> None:
        """
        Set or update the access token for API requests

        Args:
            access_token: New access token

        Example:
            >>> agent = TikTokShopAgent()
            >>> agent.set_access_token('new_token_here')
        """
        self.access_token = access_token
        if self._client is not None:
            self._client.access_token = access_token

    def generate_video_script(
        self,
        product_name: str,
        product_features: List[str],
        target_audience: str = "TCG collectors and players",
        video_type: str = "product_showcase",
        duration_seconds: int = 60
    ) -> tuple[str, Path]:
        """
        Generate TikTok video script for product promotion

        Args:
            product_name: Name of the product to feature
            product_features: List of key features to highlight
            target_audience: Target audience description
            video_type: Type of video (product_showcase, unboxing, tutorial, etc.)
            duration_seconds: Target video duration in seconds

        Returns:
            Tuple of (script_content, file_path)
        """
        features_text = "\n".join(f"- {feature}" for feature in product_features)

        prompt = f"""Create a TikTok video script for TikTok Shop:

PRODUCT: {product_name}
VIDEO TYPE: {video_type}
TARGET DURATION: {duration_seconds} seconds
TARGET AUDIENCE: {target_audience}

KEY FEATURES:
{features_text}

REQUIREMENTS:
1. Hook viewers in first 3 seconds
2. Show product in action
3. Highlight battle-ready identity
4. Include clear call-to-action (shop now)
5. Natural product placement (not overly salesy)
6. Match {self.platform_specs['video']['tone']} tone
7. Include visual direction notes
8. Add text overlay suggestions
9. Suggest background music style

Format:
[HOOK (0-3s)]
Visual: [Description]
Audio: [Script]
Text: [On-screen text]

[MAIN CONTENT (4-{duration_seconds-10}s)]
Visual: [Description]
Audio: [Script]
Text: [On-screen text]

[CALL-TO-ACTION ({duration_seconds-9}-{duration_seconds}s)]
Visual: [Description]
Audio: [Script]
Text: [On-screen text]

[MUSIC SUGGESTION]
[Background music style]

[CAPTION & HASHTAGS]
[Suggested caption and hashtags]

Write the complete video script now."""

        system_context = f"""
TIKTOK SHOP STRATEGY:

Video Strategy:
- First 3 seconds determine if viewers keep watching
- Show, don't just tell - demonstrate the product
- Authentic presentation beats polished production
- Strong CTA drives shop conversions
- Vertical format optimized for mobile viewing

Content Type: {video_type}
{self.content_strategy.get(video_type, 'Create engaging product content')}

Best Practices:
- Hook with problem or bold statement
- Use trending sounds when appropriate
- Keep text overlays short and readable
- Show product features visually
- End with clear "Shop Now" button prompt
- Tag products in video for direct purchase

TikTok Shop Features:
- In-video product tags
- Live shopping capabilities
- Creator marketplace integration
- Built-in checkout flow"""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=TIKTOK_OUTPUT_DIR / "video-scripts",
            system_context=system_context,
            metadata={
                "platform": "tiktok_shop",
                "content_type": "video_script",
                "product_name": product_name,
                "video_type": video_type,
                "duration": duration_seconds,
                "features": product_features
            }
        )

    def sync_products(
        self,
        status: Optional[str] = None,
        max_products: Optional[int] = None,
        save_to_file: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Sync products from TikTok Shop

        This method fetches all products from TikTok Shop, handling pagination
        automatically. It can optionally filter by status and limit the number
        of products retrieved.

        Args:
            status: Filter by product status ('ACTIVE', 'INACTIVE', 'DRAFT')
                   If None, fetches all products regardless of status
            max_products: Maximum number of products to sync (None for all)
            save_to_file: Whether to save synced products to a JSON file

        Returns:
            List of product dictionaries containing product information

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopAPIError: If API request fails

        Example:
            >>> agent = TikTokShopAgent(access_token='token')
            >>> # Sync all active products
            >>> products = agent.sync_products(status='ACTIVE')
            >>> print(f"Synced {len(products)} products")
            >>>
            >>> # Sync first 50 products
            >>> products = agent.sync_products(max_products=50)
        """
        client = self._get_client()

        all_products = []
        page_number = 1
        page_size = 100  # Maximum allowed by API

        while True:
            # Fetch page of products
            response = client.get_products(
                page_size=page_size,
                page_number=page_number,
                status=status
            )

            # Extract products from response
            products = response.get('data', {}).get('products', [])

            if not products:
                break

            # Add products to list
            all_products.extend(products)

            # Check if we've reached the max limit
            if max_products and len(all_products) >= max_products:
                all_products = all_products[:max_products]
                break

            # Check if there are more pages
            more_pages = response.get('data', {}).get('more', False)
            if not more_pages:
                break

            page_number += 1

        # Save to file if requested
        if save_to_file:
            import json
            output_dir = TIKTOK_OUTPUT_DIR / "products"
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status_label = f"_{status.lower()}" if status else "_all"
            filename = f"products_sync{status_label}_{timestamp}.json"
            filepath = output_dir / filename

            with open(filepath, 'w') as f:
                json.dump({
                    'synced_at': datetime.now().isoformat(),
                    'status_filter': status,
                    'total_count': len(all_products),
                    'products': all_products
                }, f, indent=2)

        return all_products

    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific product from TikTok Shop

        Args:
            product_id: TikTok Shop product ID

        Returns:
            Dictionary containing detailed product information including:
                - product_id: Product identifier
                - title: Product title/name
                - description: Product description
                - price: Product pricing information
                - inventory: Inventory/stock information
                - images: Product images
                - status: Product status
                - category: Product category
                - specifications: Product specifications

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopNotFoundError: If product not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> agent = TikTokShopAgent(access_token='token')
            >>> product = agent.get_product_details('1234567890')
            >>> print(f"Product: {product['data']['title']}")
            >>> print(f"Price: ${product['data']['price']['amount']}")
        """
        client = self._get_client()
        return client.get_product(product_id)

    def list_products(
        self,
        status: Optional[str] = None,
        page_size: int = 20,
        page_number: int = 1
    ) -> Dict[str, Any]:
        """
        Get a paginated list of products from TikTok Shop

        This is a simpler method for getting a single page of products,
        useful for iterative processing or displaying products in a UI.

        Args:
            status: Filter by product status ('ACTIVE', 'INACTIVE', 'DRAFT')
            page_size: Number of products per page (max 100)
            page_number: Page number to retrieve (starts at 1)

        Returns:
            Dictionary containing:
                - products: List of product objects
                - total: Total number of products matching filter
                - more: Boolean indicating if more pages exist

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopAPIError: If API request fails

        Example:
            >>> agent = TikTokShopAgent(access_token='token')
            >>> # Get first page of active products
            >>> result = agent.list_products(status='ACTIVE', page_size=10)
            >>> products = result['data']['products']
            >>> has_more = result['data']['more']
        """
        client = self._get_client()
        return client.get_products(
            page_size=page_size,
            page_number=page_number,
            status=status
        )

    def get_orders(
        self,
        order_status: Optional[str] = None,
        page_size: int = 20,
        page_number: int = 1,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get a paginated list of orders from TikTok Shop

        This method retrieves orders with optional filtering by status and time range.
        Useful for displaying orders in a UI or iterative processing.

        Args:
            order_status: Filter by order status (e.g., 'UNPAID', 'AWAITING_SHIPMENT',
                         'AWAITING_COLLECTION', 'IN_TRANSIT', 'DELIVERED', 'COMPLETED', 'CANCELLED')
            page_size: Number of orders per page (max 100)
            page_number: Page number to retrieve (starts at 1)
            start_time: Start time for order query (Unix timestamp in seconds)
            end_time: End time for order query (Unix timestamp in seconds)

        Returns:
            Dictionary containing:
                - orders: List of order objects
                - total: Total number of orders matching filter
                - more: Boolean indicating if more pages exist

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopAPIError: If API request fails

        Example:
            >>> agent = TikTokShopAgent(access_token='token')
            >>> # Get first page of unpaid orders
            >>> result = agent.get_orders(order_status='UNPAID', page_size=10)
            >>> orders = result['data']['orders']
            >>> has_more = result['data']['more']
        """
        client = self._get_client()
        return client.get_orders(
            order_status=order_status,
            page_size=page_size,
            page_number=page_number,
            start_time=start_time,
            end_time=end_time
        )

    def sync_orders(
        self,
        order_status: Optional[str] = None,
        max_orders: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        save_to_file: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Sync orders from TikTok Shop

        This method fetches all orders from TikTok Shop, handling pagination
        automatically. It can optionally filter by status and time range.

        Args:
            order_status: Filter by order status (e.g., 'UNPAID', 'AWAITING_SHIPMENT',
                         'IN_TRANSIT', 'DELIVERED', 'COMPLETED', 'CANCELLED')
            max_orders: Maximum number of orders to sync (None for all)
            start_time: Start time for order query (Unix timestamp in seconds)
            end_time: End time for order query (Unix timestamp in seconds)
            save_to_file: Whether to save synced orders to a JSON file

        Returns:
            List of order dictionaries containing order information

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopAPIError: If API request fails

        Example:
            >>> agent = TikTokShopAgent(access_token='token')
            >>> # Sync all unpaid orders
            >>> orders = agent.sync_orders(order_status='UNPAID')
            >>> print(f"Synced {len(orders)} orders")
            >>>
            >>> # Sync orders from last 7 days
            >>> import time
            >>> end_time = int(time.time())
            >>> start_time = end_time - (7 * 24 * 60 * 60)
            >>> orders = agent.sync_orders(start_time=start_time, end_time=end_time)
        """
        client = self._get_client()

        all_orders = []
        page_number = 1
        page_size = 100  # Maximum allowed by API

        while True:
            # Fetch page of orders
            response = client.get_orders(
                order_status=order_status,
                page_size=page_size,
                page_number=page_number,
                start_time=start_time,
                end_time=end_time
            )

            # Extract orders from response
            orders = response.get('data', {}).get('orders', [])

            if not orders:
                break

            # Add orders to list
            all_orders.extend(orders)

            # Check if we've reached the max limit
            if max_orders and len(all_orders) >= max_orders:
                all_orders = all_orders[:max_orders]
                break

            # Check if there are more pages
            more_pages = response.get('data', {}).get('more', False)
            if not more_pages:
                break

            page_number += 1

        # Save to file if requested
        if save_to_file:
            import json
            output_dir = TIKTOK_OUTPUT_DIR / "orders"
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            status_label = f"_{order_status.lower()}" if order_status else "_all"
            filename = f"orders_sync{status_label}_{timestamp}.json"
            filepath = output_dir / filename

            with open(filepath, 'w') as f:
                json.dump({
                    'synced_at': datetime.now().isoformat(),
                    'status_filter': order_status,
                    'start_time': start_time,
                    'end_time': end_time,
                    'total_count': len(all_orders),
                    'orders': all_orders
                }, f, indent=2)

        return all_orders

    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific order from TikTok Shop

        Args:
            order_id: TikTok Shop order ID

        Returns:
            Dictionary containing detailed order information including:
                - order_id: Order identifier
                - status: Order status
                - buyer_info: Buyer information
                - items: Ordered items with details
                - payment: Payment information
                - shipping: Shipping address and status
                - timestamps: Creation, payment, shipment times

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopNotFoundError: If order not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> agent = TikTokShopAgent(access_token='token')
            >>> order = agent.get_order_details('1234567890')
            >>> print(f"Order Status: {order['data']['status']}")
            >>> print(f"Total: ${order['data']['payment']['total_amount']}")
        """
        client = self._get_client()
        return client.get_order(order_id)

    def process_order_data(
        self,
        orders: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process and analyze order data to extract insights

        This method takes a list of orders and generates useful analytics
        such as total revenue, order counts by status, popular products, etc.

        Args:
            orders: List of order dictionaries (from get_orders or sync_orders)

        Returns:
            Dictionary containing processed order analytics:
                - total_orders: Total number of orders
                - orders_by_status: Count of orders grouped by status
                - total_revenue: Total revenue from all orders
                - top_products: Most ordered products
                - order_value_stats: Min, max, average order values

        Example:
            >>> agent = TikTokShopAgent(access_token='token')
            >>> orders = agent.sync_orders()
            >>> analytics = agent.process_order_data(orders)
            >>> print(f"Total Revenue: ${analytics['total_revenue']}")
            >>> print(f"Total Orders: {analytics['total_orders']}")
        """
        if not orders:
            return {
                'total_orders': 0,
                'orders_by_status': {},
                'total_revenue': 0.0,
                'top_products': [],
                'order_value_stats': {
                    'min': 0.0,
                    'max': 0.0,
                    'average': 0.0
                }
            }

        # Initialize analytics
        orders_by_status = {}
        total_revenue = 0.0
        product_counts = {}
        order_values = []

        # Process each order
        for order in orders:
            # Count orders by status
            status = order.get('status', 'UNKNOWN')
            orders_by_status[status] = orders_by_status.get(status, 0) + 1

            # Calculate revenue (only from completed/paid orders)
            if status not in ['UNPAID', 'CANCELLED']:
                payment_info = order.get('payment', {})
                order_total = float(payment_info.get('total_amount', 0))
                total_revenue += order_total
                order_values.append(order_total)

            # Count product occurrences
            items = order.get('items', [])
            for item in items:
                product_id = item.get('product_id')
                product_name = item.get('product_name', 'Unknown')
                quantity = int(item.get('quantity', 1))

                if product_id:
                    if product_id not in product_counts:
                        product_counts[product_id] = {
                            'product_name': product_name,
                            'count': 0
                        }
                    product_counts[product_id]['count'] += quantity

        # Get top products
        top_products = sorted(
            [
                {
                    'product_id': pid,
                    'product_name': info['product_name'],
                    'total_ordered': info['count']
                }
                for pid, info in product_counts.items()
            ],
            key=lambda x: x['total_ordered'],
            reverse=True
        )[:10]  # Top 10 products

        # Calculate order value statistics
        order_value_stats = {
            'min': min(order_values) if order_values else 0.0,
            'max': max(order_values) if order_values else 0.0,
            'average': sum(order_values) / len(order_values) if order_values else 0.0
        }

        return {
            'total_orders': len(orders),
            'orders_by_status': orders_by_status,
            'total_revenue': round(total_revenue, 2),
            'top_products': top_products,
            'order_value_stats': {
                'min': round(order_value_stats['min'], 2),
                'max': round(order_value_stats['max'], 2),
                'average': round(order_value_stats['average'], 2)
            }
        }

    def get_analytics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get shop analytics and performance metrics from TikTok Shop

        This method fetches comprehensive analytics data including sales metrics,
        traffic data, conversion rates, and other performance indicators.

        Args:
            start_date: Start date for analytics period (format: 'YYYY-MM-DD')
                       If None, defaults to last 30 days
            end_date: End date for analytics period (format: 'YYYY-MM-DD')
                     If None, defaults to today
            metrics: List of specific metrics to retrieve. If None, gets all available.
                    Common metrics include: 'sales', 'views', 'clicks', 'conversion_rate',
                    'average_order_value', 'total_revenue'

        Returns:
            Dictionary containing analytics data:
                - period: Date range for the analytics
                - metrics: Dictionary of metric name -> value
                - trends: Performance trends over time
                - comparisons: Period-over-period comparisons

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopAPIError: If API request fails

        Example:
            >>> agent = TikTokShopAgent(access_token='token')
            >>> # Get last 30 days of analytics
            >>> analytics = agent.get_analytics()
            >>> print(f"Total Revenue: ${analytics['metrics']['total_revenue']}")
            >>> print(f"Conversion Rate: {analytics['metrics']['conversion_rate']}%")
            >>>
            >>> # Get specific date range
            >>> analytics = agent.get_analytics(
            ...     start_date='2024-01-01',
            ...     end_date='2024-01-31',
            ...     metrics=['sales', 'revenue']
            ... )
        """
        client = self._get_client()

        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_datetime = datetime.now() - timedelta(days=30)
            start_date = start_datetime.strftime('%Y-%m-%d')

        # Fetch analytics from TikTok Shop API
        return client.get_analytics(
            start_date=start_date,
            end_date=end_date,
            metrics=metrics
        )

    def get_product_analytics(
        self,
        product_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for a specific product

        This method retrieves performance metrics for an individual product,
        including views, sales, conversion rates, and revenue.

        Args:
            product_id: TikTok Shop product ID
            start_date: Start date for analytics period (format: 'YYYY-MM-DD')
                       If None, defaults to last 30 days
            end_date: End date for analytics period (format: 'YYYY-MM-DD')
                     If None, defaults to today

        Returns:
            Dictionary containing product analytics:
                - product_id: Product identifier
                - product_name: Product name
                - period: Date range for the analytics
                - views: Number of product views
                - clicks: Number of product clicks
                - conversions: Number of purchases
                - conversion_rate: Percentage of clicks that converted
                - revenue: Total revenue from product
                - units_sold: Total units sold
                - average_price: Average selling price

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopNotFoundError: If product not found
            TikTokShopAPIError: If API request fails

        Example:
            >>> agent = TikTokShopAgent(access_token='token')
            >>> analytics = agent.get_product_analytics('1234567890')
            >>> print(f"Product Views: {analytics['views']}")
            >>> print(f"Conversion Rate: {analytics['conversion_rate']}%")
            >>> print(f"Total Revenue: ${analytics['revenue']}")
        """
        client = self._get_client()

        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_datetime = datetime.now() - timedelta(days=30)
            start_date = start_datetime.strftime('%Y-%m-%d')

        # Fetch product analytics from TikTok Shop API
        return client.get_product_analytics(
            product_id=product_id,
            start_date=start_date,
            end_date=end_date
        )

    def get_shop_performance(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get overall shop performance metrics

        This method retrieves high-level performance indicators for the entire shop,
        including total sales, customer metrics, and operational statistics.

        Args:
            start_date: Start date for performance period (format: 'YYYY-MM-DD')
                       If None, defaults to last 30 days
            end_date: End date for performance period (format: 'YYYY-MM-DD')
                     If None, defaults to today

        Returns:
            Dictionary containing shop performance metrics:
                - period: Date range for the metrics
                - total_revenue: Total revenue for the period
                - total_orders: Total number of orders
                - total_units_sold: Total units sold
                - average_order_value: Average value per order
                - customer_metrics: Customer acquisition and retention data
                - fulfillment_metrics: Shipping and delivery performance
                - return_rate: Percentage of orders returned
                - cancellation_rate: Percentage of orders cancelled
                - shop_rating: Overall shop rating
                - response_time: Average customer service response time

        Raises:
            TikTokShopAuthError: If authentication fails
            TikTokShopAPIError: If API request fails

        Example:
            >>> agent = TikTokShopAgent(access_token='token')
            >>> performance = agent.get_shop_performance()
            >>> print(f"Total Revenue: ${performance['total_revenue']}")
            >>> print(f"Average Order Value: ${performance['average_order_value']}")
            >>> print(f"Shop Rating: {performance['shop_rating']}/5")
            >>>
            >>> # Get specific date range
            >>> performance = agent.get_shop_performance(
            ...     start_date='2024-01-01',
            ...     end_date='2024-01-31'
            ... )
        """
        client = self._get_client()

        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_datetime = datetime.now() - timedelta(days=30)
            start_date = start_datetime.strftime('%Y-%m-%d')

        # Fetch shop performance from TikTok Shop API
        return client.get_shop_performance(
            start_date=start_date,
            end_date=end_date
        )
