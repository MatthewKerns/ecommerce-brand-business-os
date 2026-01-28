"""
Competitor Analysis Agent
Analyzes competitor content, listings, and strategies
"""
from pathlib import Path
from typing import Optional, List, Dict
from .base_agent import BaseAgent
from config.config import COMPETITOR_OUTPUT_DIR


class CompetitorAgent(BaseAgent):
    """Agent specialized in competitor analysis"""

    def __init__(self):
        super().__init__(agent_name="competitor_agent")

    def analyze_competitor_listing(
        self,
        competitor_name: str,
        product_title: str,
        bullet_points: List[str],
        description: str,
        price: Optional[float] = None,
        rating: Optional[float] = None,
        review_count: Optional[int] = None
    ) -> tuple[str, Path]:
        """
        Analyze a competitor's Amazon listing

        Args:
            competitor_name: Competitor brand name
            product_title: Their product title
            bullet_points: Their bullet points
            description: Their product description
            price: Product price
            rating: Star rating
            review_count: Number of reviews

        Returns:
            Tuple of (analysis, file_path)
        """
        bullets_text = "\n".join([f"{i+1}. {b}" for i, b in enumerate(bullet_points)])
        metrics_text = ""
        if price:
            metrics_text += f"\nPRICE: ${price}"
        if rating:
            metrics_text += f"\nRATING: {rating}/5 stars"
        if review_count:
            metrics_text += f"\nREVIEWS: {review_count}"

        prompt = f"""Analyze this competitor listing:

COMPETITOR: {competitor_name}
{metrics_text}

TITLE:
{product_title}

BULLETS:
{bullets_text}

DESCRIPTION:
{description}

ANALYSIS FRAMEWORK:

1. POSITIONING ANALYSIS
   - How do they position the product?
   - What customer identity are they selling to?
   - Commodity vs. premium positioning?
   - Emotional vs. functional focus?

2. KEYWORD STRATEGY
   - What keywords are they targeting?
   - Front-loaded terms?
   - Search optimization level?
   - Missing opportunities?

3. MESSAGING ANALYSIS
   - Brand voice and tone?
   - Benefits vs. features ratio?
   - Unique selling propositions?
   - Pain points addressed?

4. DIFFERENTIATION OPPORTUNITIES
   - Where are they weak?
   - What are they NOT saying?
   - How can Infinity Vault stand out?
   - Gaps we can exploit?

5. PRICING STRATEGY
   - Premium, mid-tier, or budget?
   - Value perception?
   - Quality signals?

6. CONVERSION OPTIMIZATION
   - Trust signals (warranty, guarantees)?
   - Social proof?
   - Urgency or scarcity?
   - Call-to-action strength?

7. RECOMMENDATIONS FOR INFINITY VAULT
   - What to adopt (best practices)?
   - What to avoid (their mistakes)?
   - How to differentiate?
   - Specific improvements for our listing?

FORMAT:
## COMPETITOR OVERVIEW
[Summary of their approach]

## DETAILED ANALYSIS
[Go through each framework point]

## STRENGTHS
[What they do well]

## WEAKNESSES
[Where they fall short]

## DIFFERENTIATION STRATEGY
[How Infinity Vault can stand out]

## ACTION ITEMS
[Specific recommendations for our listings]

Write the complete competitive analysis now."""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=COMPETITOR_OUTPUT_DIR,
            filename=f"competitor_{competitor_name.replace(' ', '_')}_analysis.md",
            metadata={
                "competitor": competitor_name,
                "price": price,
                "rating": rating,
                "review_count": review_count
            },
            max_tokens=4096
        )

    def analyze_competitor_reviews(
        self,
        competitor_name: str,
        positive_reviews: List[str],
        negative_reviews: List[str]
    ) -> tuple[str, Path]:
        """
        Analyze competitor reviews for insights

        Args:
            competitor_name: Competitor name
            positive_reviews: List of positive review excerpts
            negative_reviews: List of negative review excerpts

        Returns:
            Tuple of (analysis, file_path)
        """
        positive_text = "\n".join([f"- {r}" for r in positive_reviews])
        negative_text = "\n".join([f"- {r}" for r in negative_reviews])

        prompt = f"""Analyze competitor reviews:

COMPETITOR: {competitor_name}

POSITIVE REVIEWS (What customers love):
{positive_text}

NEGATIVE REVIEWS (What customers complain about):
{negative_text}

ANALYSIS REQUIREMENTS:

1. CUSTOMER DESIRES (from positive reviews)
   - What do customers value most?
   - What language do they use to describe benefits?
   - Emotional vs. functional satisfaction?
   - Common themes in praise?

2. PAIN POINTS (from negative reviews)
   - What are the most common complaints?
   - Quality issues?
   - Unmet expectations?
   - Feature gaps?

3. VOICE OF CUSTOMER
   - How do customers describe the product?
   - What words/phrases do they use repeatedly?
   - What outcomes do they care about?
   - What language resonates?

4. PRODUCT OPPORTUNITY GAPS
   - What do customers wish existed?
   - Features they want?
   - Improvements they suggest?
   - Unmet needs?

5. MESSAGING INSIGHTS
   - What should Infinity Vault emphasize?
   - What pain points to address?
   - What benefits to highlight?
   - What language to use in copy?

6. PRODUCT DEVELOPMENT IDEAS
   - Features to add/improve
   - Quality standards to exceed
   - Service enhancements
   - Warranty/guarantee opportunities

FORMAT:
## KEY INSIGHTS
[High-level takeaways]

## CUSTOMER DESIRES
[What they want]

## PAIN POINTS
[What frustrates them]

## VOICE OF CUSTOMER LANGUAGE
[Exact phrases to use in marketing]

## OPPORTUNITIES FOR INFINITY VAULT
[How to differentiate and win]

## ACTION ITEMS
[Specific recommendations]

Write the complete review analysis now."""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=COMPETITOR_OUTPUT_DIR,
            filename=f"competitor_{competitor_name.replace(' ', '_')}_reviews.md",
            metadata={
                "competitor": competitor_name,
                "positive_count": len(positive_reviews),
                "negative_count": len(negative_reviews)
            },
            max_tokens=4096
        )

    def compare_multiple_competitors(
        self,
        competitors: List[Dict[str, any]]
    ) -> tuple[str, Path]:
        """
        Compare multiple competitors side-by-side

        Args:
            competitors: List of competitor dicts with keys:
                - name
                - price
                - rating
                - positioning
                - key_features
                - weaknesses

        Returns:
            Tuple of (comparison, file_path)
        """
        comp_text = "\n\n".join([
            f"""COMPETITOR {i+1}: {c['name']}
- Price: ${c.get('price', 'Unknown')}
- Rating: {c.get('rating', 'Unknown')}/5
- Positioning: {c.get('positioning', 'Unknown')}
- Key Features: {c.get('key_features', 'Unknown')}
- Weaknesses: {c.get('weaknesses', 'Unknown')}"""
            for i, c in enumerate(competitors)
        ])

        prompt = f"""Create a competitive comparison analysis:

COMPETITORS:
{comp_text}

COMPARISON FRAMEWORK:

1. MARKET SEGMENTATION
   - Where does each competitor position?
   - Price tiers (budget, mid-tier, premium)
   - Target audiences
   - Market gaps

2. POSITIONING MAP
   - Who's commodity vs. premium?
   - Who's functional vs. emotional?
   - Where is there white space?
   - Where should Infinity Vault position?

3. FEATURE COMPARISON
   - What features are table stakes?
   - What features differentiate?
   - What's missing from everyone?
   - Innovation opportunities

4. MESSAGING COMPARISON
   - How does each brand communicate?
   - Voice and tone differences
   - Emotional vs. rational appeals
   - Messaging gaps

5. PRICING STRATEGY
   - Price distribution
   - Value perception
   - Premium positioning opportunities
   - Competitive pricing recommendation

6. STRENGTHS & WEAKNESSES MATRIX
   - Each competitor's advantages
   - Each competitor's vulnerabilities
   - Attack opportunities
   - Defensive needs

7. INFINITY VAULT DIFFERENTIATION STRATEGY
   - Where to compete
   - Where to avoid competition
   - Unique positioning
   - Messaging strategy
   - Feature priorities
   - Pricing recommendation

FORMAT:
## MARKET OVERVIEW
[Industry landscape]

## COMPETITIVE MATRIX
[Side-by-side comparison table]

## POSITIONING MAP
[Where each brand sits]

## INFINITY VAULT STRATEGY
[How to win]

## ACTION PLAN
[Specific next steps]

Write the complete competitive comparison now."""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=COMPETITOR_OUTPUT_DIR,
            filename="competitive_landscape_analysis.md",
            metadata={
                "competitors_analyzed": [c['name'] for c in competitors],
                "num_competitors": len(competitors)
            },
            max_tokens=4096
        )

    def identify_content_gaps(
        self,
        competitor_content: List[Dict[str, str]]
    ) -> tuple[str, Path]:
        """
        Identify content opportunities based on competitor content

        Args:
            competitor_content: List of dicts with:
                - competitor_name
                - content_type (blog, social, video, etc.)
                - topic
                - performance (optional)

        Returns:
            Tuple of (gap_analysis, file_path)
        """
        content_text = "\n\n".join([
            f"""- {c['competitor_name']}: {c['content_type']} on '{c['topic']}' {f"(Performance: {c.get('performance', 'Unknown')})" if 'performance' in c else ''}"""
            for c in competitor_content
        ])

        prompt = f"""Analyze competitor content to find gaps:

COMPETITOR CONTENT:
{content_text}

ANALYSIS REQUIREMENTS:

1. CONTENT THEMES
   - What topics are competitors covering?
   - What themes are popular?
   - What's oversaturated?
   - What's underserved?

2. CONTENT FORMATS
   - What formats are they using?
   - Video, blog, social, etc.
   - What's missing?
   - Format opportunities

3. QUALITY ASSESSMENT
   - Production quality
   - Depth of content
   - Value provided
   - Engagement level

4. CONTENT GAPS
   - Topics no one is covering
   - Underserved audiences
   - Unexplored angles
   - Format opportunities

5. INFINITY VAULT OPPORTUNITIES
   - High-value, low-competition topics
   - Content series ideas
   - Unique angles using battle-ready positioning
   - Format innovations

6. CONTENT STRATEGY RECOMMENDATIONS
   - Priority topics to create
   - Content calendar suggestions
   - Resource allocation
   - Distribution strategy

FORMAT:
## COMPETITIVE CONTENT LANDSCAPE
[What's out there]

## CONTENT GAPS
[What's missing]

## OPPORTUNITY AREAS
[Where to focus]

## RECOMMENDED CONTENT CALENDAR
[Specific content ideas]

## EXECUTION PLAN
[How to create and distribute]

Write the complete content gap analysis now."""

        return self.generate_and_save(
            prompt=prompt,
            output_dir=COMPETITOR_OUTPUT_DIR,
            filename="content_gap_analysis.md",
            metadata={
                "content_pieces_analyzed": len(competitor_content)
            },
            max_tokens=4096
        )
