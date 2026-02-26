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
