"""
Amazon Listing Optimization Agent
Creates and optimizes Amazon product listings with brand voice
"""
from pathlib import Path
from typing import Optional, List, Dict
from .base_agent import BaseAgent
from config.config import AMAZON_OUTPUT_DIR


class AmazonAgent(BaseAgent):
    """Agent specialized in Amazon listing optimization"""

    def __init__(self):
        super().__init__(agent_name="amazon_agent")

    def generate_product_title(
        self,
        product_name: str,
        key_features: List[str],
        target_keywords: List[str]
    ) -> tuple[str, Path]:
        """
        Generate optimized Amazon product title

        Args:
            product_name: Product name
            key_features: Main features to highlight
            target_keywords: SEO keywords to include

        Returns:
            Tuple of (title, file_path)
        """
        prompt = f"""Create an optimized Amazon product title:

PRODUCT: {product_name}
KEY FEATURES: {', '.join(key_features)}
TARGET KEYWORDS: {', '.join(target_keywords)}

AMAZON TITLE FORMULA:
[Value Signal] + [Category] + [Differentiator] + [Benefit]

REQUIREMENTS:
1. Under 200 characters (Amazon limit)
2. Front-load most important keywords
3. Include key features
4. Clear differentiation
5. Benefit-focused
6. Search-optimized but readable

BRAND POSITIONING:
- Battle-Ready Equipment (not commodity storage)
- Professional-grade quality
- Tournament-tested
- Lifetime warranty

Examples of good titles:
- "Premium Trading Card Binder - Scratch-Resistant 9-Pocket Pages - Battle-Ready Storage for Pokemon, MTG, Sports Cards - Professional Grade with Lifetime Warranty"

Write 3 title variations, then select the best one.

FORMAT:
OPTION 1: [title]
OPTION 2: [title]
OPTION 3: [title]

RECOMMENDED: [best option with brief explanation why]"""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=AMAZON_OUTPUT_DIR,
            filename=f"title_{product_name.replace(' ', '_')}.md",
            metadata={
                "product_name": product_name,
                "key_features": key_features,
                "target_keywords": target_keywords
            }
        )

    def generate_bullet_points(
        self,
        product_name: str,
        features: List[Dict[str, str]],
        target_audience: str = "Tournament players and serious collectors"
    ) -> tuple[str, Path]:
        """
        Generate Amazon bullet points (5 bullets)

        Args:
            product_name: Product name
            features: List of dicts with 'feature' and 'benefit' keys
            target_audience: Who this is for

        Returns:
            Tuple of (bullets, file_path)
        """
        features_text = "\n".join([f"- Feature: {f.get('feature', '')}, Benefit: {f.get('benefit', '')}" for f in features])

        prompt = f"""Create 5 Amazon bullet points for:

PRODUCT: {product_name}
TARGET AUDIENCE: {target_audience}

FEATURES & BENEFITS:
{features_text}

BULLET POINT STRUCTURE:
[BENEFIT] → [FEATURE] → [EMOTIONAL PAYOFF]

REQUIREMENTS:
1. Each bullet under 200 characters
2. Start with benefit/outcome (not feature)
3. Use emotional language (battle-ready, confident, prepared)
4. Include features as proof points
5. Connect to customer identity (serious player, not casual hobbyist)
6. Use power words (premium, professional, tournament-grade)
7. Maintain brand voice (confident but not arrogant)

EXAMPLE FORMAT:
• SHOW UP BATTLE READY - Premium scratch-resistant pages keep your collection pristine so you arrive at every tournament with confidence and pride in your gear

CRITICAL:
- Focus on transformation (who they become using this)
- Use fantasy/gaming language naturally
- Make them feel like serious players
- Build desire, not just inform

Write all 5 bullets now."""

        system_context = """
AMAZON BULLET POINT STRATEGY:

Psychology:
- Customers buy who they want to be, not what they need
- "Serious player" identity is the core desire
- Battle-ready = prepared, confident, respected

Formula:
1. Emotional benefit (feel confident, prepared, respected)
2. Functional feature (scratch-resistant, durable, etc.)
3. Outcome/payoff (protect your investment, win tournaments)

Language Principles:
- Active voice
- Second person ("you" not "we")
- Specific not generic
- Evocative not boring

Positioning:
- This is battle-ready equipment
- Not commodity storage
- Professional-grade quality
- Tournament-tested"""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=AMAZON_OUTPUT_DIR,
            system_context=system_context,
            filename=f"bullets_{product_name.replace(' ', '_')}.md",
            metadata={
                "product_name": product_name,
                "features": features,
                "target_audience": target_audience
            }
        )

    def generate_product_description(
        self,
        product_name: str,
        long_description: str,
        usp: str,
        warranty_info: Optional[str] = "Lifetime warranty"
    ) -> tuple[str, Path]:
        """
        Generate Amazon product description

        Args:
            product_name: Product name
            long_description: Detailed product information
            usp: Unique selling proposition
            warranty_info: Warranty details

        Returns:
            Tuple of (description, file_path)
        """
        prompt = f"""Create an Amazon product description:

PRODUCT: {product_name}
UNIQUE SELLING PROPOSITION: {usp}
WARRANTY: {warranty_info}

PRODUCT DETAILS:
{long_description}

REQUIREMENTS:
1. Engaging opening that hooks readers
2. Tell the brand story (Infinity Vault = Battle-Ready Equipment)
3. Highlight unique features and benefits
4. Address customer pain points
5. Build trust (warranty, quality guarantees)
6. Include specifications clearly
7. End with compelling call-to-action
8. Use HTML formatting allowed on Amazon:
   - <b>Bold</b> for emphasis
   - Line breaks for readability
   - Bullet lists where appropriate

STRUCTURE:
1. Hook (1-2 sentences)
2. Brand story/positioning (2-3 sentences)
3. Key benefits (bullet format)
4. Features & specifications
5. Quality guarantee/warranty
6. Call-to-action

TONE:
- Confident and aspirational
- Professional but passionate
- Focus on transformation (who they become)
- Battle-ready mindset throughout

Write the complete product description now."""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=AMAZON_OUTPUT_DIR,
            filename=f"description_{product_name.replace(' ', '_')}.md",
            metadata={
                "product_name": product_name,
                "usp": usp,
                "warranty": warranty_info
            }
        )

    def generate_a_plus_content(
        self,
        product_name: str,
        modules: List[str]
    ) -> tuple[str, Path]:
        """
        Generate Amazon A+ Content sections

        Args:
            product_name: Product name
            modules: List of A+ module types to create

        Returns:
            Tuple of (a_plus_content, file_path)
        """
        modules_text = "\n".join([f"- {m}" for m in modules])

        prompt = f"""Create Amazon A+ Content for:

PRODUCT: {product_name}

MODULES TO CREATE:
{modules_text}

For each module, provide:
1. Module name/type
2. Headline text
3. Body copy
4. Image direction (what visuals should show)
5. Design notes

COMMON A+ MODULES:
- Hero image with headline
- Feature comparison chart
- Product benefits grid (4-panel)
- Lifestyle imagery with text
- Technical specifications
- Brand story section
- Customer testimonials/social proof

REQUIREMENTS:
- Visually compelling
- Battle-ready positioning throughout
- High-quality imagery direction
- Scannable text (short paragraphs, bullets)
- Consistent brand voice
- Emphasize premium quality and professional use

Write the complete A+ Content plan now."""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=AMAZON_OUTPUT_DIR,
            filename=f"aplus_{product_name.replace(' ', '_')}.md",
            metadata={
                "product_name": product_name,
                "modules": modules
            }
        )

    def optimize_existing_listing(
        self,
        current_title: str,
        current_bullets: List[str],
        current_description: str,
        performance_data: Optional[Dict] = None
    ) -> tuple[str, Path]:
        """
        Analyze and optimize an existing listing

        Args:
            current_title: Current product title
            current_bullets: Current bullet points
            current_description: Current description
            performance_data: Optional dict with CTR, conversion rate, etc.

        Returns:
            Tuple of (optimization_report, file_path)
        """
        bullets_text = "\n".join([f"{i+1}. {b}" for i, b in enumerate(current_bullets)])
        perf_text = f"\n\nPERFORMANCE DATA:\n{performance_data}" if performance_data else ""

        prompt = f"""Analyze and optimize this Amazon listing:

CURRENT TITLE:
{current_title}

CURRENT BULLETS:
{bullets_text}

CURRENT DESCRIPTION:
{current_description}
{perf_text}

ANALYSIS REQUIREMENTS:
1. Keyword optimization (are key terms present and front-loaded?)
2. Brand voice alignment (does it sound like Infinity Vault?)
3. Benefit focus (selling identity or just features?)
4. Emotional resonance (battle-ready positioning?)
5. Competitive differentiation (stands out from commodity storage?)
6. Conversion optimization (clear CTA, urgency, trust signals?)

PROVIDE:
1. Current state assessment (what's working, what's not)
2. Specific recommendations for each element
3. Rewritten versions incorporating feedback
4. A/B test suggestions

FORMAT:
## ANALYSIS
[Detailed analysis of current listing]

## RECOMMENDATIONS
[Specific improvements]

## OPTIMIZED VERSIONS
### Title
[New title]

### Bullets
[5 new bullets]

### Description
[New description]

## A/B TEST SUGGESTIONS
[What to test]

Write the complete optimization report now."""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=AMAZON_OUTPUT_DIR,
            filename="listing_optimization_report.md",
            metadata={
                "current_title": current_title,
                "performance_data": performance_data
            },
            max_tokens=4096
        )

    def generate_backend_keywords(
        self,
        product_name: str,
        category: str,
        target_use_cases: List[str]
    ) -> tuple[str, Path]:
        """
        Generate Amazon backend search terms

        Args:
            product_name: Product name
            category: Product category
            target_use_cases: How customers use the product

        Returns:
            Tuple of (keywords, file_path)
        """
        use_cases_text = ", ".join(target_use_cases)

        prompt = f"""Generate Amazon backend search terms:

PRODUCT: {product_name}
CATEGORY: {category}
USE CASES: {use_cases_text}

REQUIREMENTS:
1. Under 250 bytes (Amazon limit)
2. No duplicate words from title/bullets
3. Include common misspellings
4. Competitor brand names (generic terms only)
5. Synonym variations
6. Related search terms
7. Use-case keywords
8. No punctuation (space-separated)

CATEGORIES TO COVER:
- Product types (binder, storage, case, etc.)
- Materials (leather, vinyl, plastic, etc.)
- Use cases (tournament, collection, display, etc.)
- Card types (pokemon, mtg, yugioh, sports, etc.)
- Features (protective, durable, portable, etc.)
- Benefits (organize, protect, display, etc.)

FORMAT:
[Space-separated keyword list under 250 bytes]

Then provide:
- Byte count
- Keyword categories included

Write the backend keywords now."""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=AMAZON_OUTPUT_DIR,
            filename=f"backend_keywords_{product_name.replace(' ', '_')}.md",
            metadata={
                "product_name": product_name,
                "category": category
            }
        )
