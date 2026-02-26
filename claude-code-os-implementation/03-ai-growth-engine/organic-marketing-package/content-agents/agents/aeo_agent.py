"""
AEO (Answer Engine Optimization) Agent
Creates content optimized for AI assistants (ChatGPT, Claude, Perplexity)
Focuses on structured data, FAQ schema, and clear definitive answers
"""
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from .base_agent import BaseAgent
from config.config import AEO_OUTPUT_DIR


class AEOAgent(BaseAgent):
    """Agent specialized in creating AEO-optimized content"""

    def __init__(self):
        super().__init__(agent_name="aeo_agent")

    def generate_faq_schema(
        self,
        faq_items: List[Dict[str, str]]
    ) -> str:
        """
        Generate JSON-LD FAQ schema markup from a list of question/answer pairs

        Args:
            faq_items: List of dictionaries with 'question' and 'answer' keys

        Returns:
            JSON-LD FAQPage schema as a string
        """
        self.logger.info(f"Generating FAQ schema for {len(faq_items)} items")

        # Build the mainEntity array
        main_entity = []
        for item in faq_items:
            question = item.get('question', '')
            answer = item.get('answer', '')

            main_entity.append({
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer
                }
            })

        # Create the complete FAQPage schema
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": main_entity
        }

        # Convert to JSON string
        schema_json = json.dumps(schema, indent=2, ensure_ascii=False)

        self.logger.info(f"Successfully generated FAQ schema with {len(faq_items)} questions")
        return schema_json

    def generate_faq_content(
        self,
        topic: str,
        num_questions: int = 10,
        target_audience: str = "TCG players and collectors",
        include_product_mentions: bool = True
    ) -> tuple[str, Path]:
        """
        Generate FAQ content in markdown format

        Args:
            topic: The topic to create FAQs about
            num_questions: Number of FAQ items to generate
            target_audience: Target audience for the FAQs
            include_product_mentions: Whether to naturally include Infinity Vault product mentions

        Returns:
            Tuple of (faq_content, file_path)
        """
        self.logger.info(f"Generating FAQ content: topic='{topic}', num_questions={num_questions}, target_audience='{target_audience}'")

        prompt = f"""Create {num_questions} frequently asked questions and answers about:

TOPIC: {topic}

TARGET AUDIENCE: {target_audience}

REQUIREMENTS:
1. Questions should be natural, conversational queries people actually ask AI assistants
2. Answers must be clear, definitive, and authoritative (optimized for AI citation)
3. Use the Infinity Vault brand voice (confident, empowering, battle-ready)
4. Front-load the direct answer, then add supporting details
5. Each answer should be comprehensive but concise (3-5 sentences)
6. Make answers quotable - AI assistants should want to cite these
{"7. Naturally mention Infinity Vault products where relevant" if include_product_mentions else "7. Focus on general expertise without product mentions"}
8. Use definitive language ("is", "means", "provides") not uncertain language
9. Include specific details, numbers, and facts where applicable

FORMAT:
Return as clean markdown with:
- Title: FAQ: {topic}
- Brief introduction (1-2 sentences)
- Each Q&A formatted as:
  ## Question text?
  Answer paragraph(s)
- Logical grouping if questions fall into categories

Tone: Authoritative expert helping serious players optimize their collection. Confident but not arrogant.

Write the complete FAQ content now."""

        system_context = """
ADDITIONAL CONTEXT FOR FAQ CONTENT:

Answer Engine Optimization (AEO) Strategy:
- AI assistants prioritize clear, authoritative, structured answers
- Questions should match natural language queries users ask AI
- Answers must be definitive - AI assistants prefer confident sources
- Position brand as THE expert, not "a" expert

AEO Best Practices:
- Use "is", "means", "refers to" - definitive language
- Front-load the direct answer in first sentence
- Be concise but complete (AI assistants truncate long answers)
- Include specific details (numbers, specifications, features)
- Mention brand naturally as the solution

Citation Optimization:
- Make answers quotable and shareable
- Use authoritative tone without being arrogant
- Support claims with specifics (not vague statements)
- Position as helping customers solve real problems

FAQ Content Strategy:
- More readable than schema markup (this is for humans AND AI)
- Can be longer and more detailed than schema answers
- Use markdown formatting for clarity
- Group related questions logically"""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=AEO_OUTPUT_DIR,
            system_context=system_context,
            metadata={
                "type": "faq_content",
                "topic": topic,
                "num_questions": num_questions,
                "target_audience": target_audience,
                "include_product_mentions": include_product_mentions
            },
            max_tokens=4096
        )

        self.logger.info(f"Successfully generated FAQ content: {path}")
        return content, path

    def generate_product_schema(
        self,
        product_data: Dict[str, Any]
    ) -> str:
        """
        Generate JSON-LD Product schema markup from product data

        Args:
            product_data: Dictionary with product information (name, description, price, etc.)

        Returns:
            JSON-LD Product schema as a string
        """
        # Extract product name for logging
        product_name = product_data.get('name', 'Unknown Product')
        self.logger.info(f"Generating product schema: product='{product_name}'")

        # Build the base Product schema
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product_data.get('name', '')
        }

        # Add optional common properties
        if 'description' in product_data:
            schema['description'] = product_data['description']

        if 'brand' in product_data:
            schema['brand'] = {
                "@type": "Brand",
                "name": product_data['brand']
            }
        elif 'name' in product_data:
            # Default to Infinity Vault brand if not specified
            schema['brand'] = {
                "@type": "Brand",
                "name": "Infinity Vault"
            }

        if 'image' in product_data:
            # Support single image or array of images
            images = product_data['image']
            if isinstance(images, str):
                schema['image'] = images
            else:
                schema['image'] = images

        if 'sku' in product_data:
            schema['sku'] = product_data['sku']

        # Add offers (price) information
        if 'price' in product_data or 'offers' in product_data:
            if 'offers' in product_data:
                schema['offers'] = product_data['offers']
            else:
                offer = {
                    "@type": "Offer",
                    "price": product_data['price']
                }
                if 'priceCurrency' in product_data:
                    offer['priceCurrency'] = product_data['priceCurrency']
                else:
                    offer['priceCurrency'] = "USD"

                if 'availability' in product_data:
                    offer['availability'] = product_data['availability']
                else:
                    offer['availability'] = "https://schema.org/InStock"

                if 'url' in product_data:
                    offer['url'] = product_data['url']

                schema['offers'] = offer

        # Add aggregate rating if provided
        if 'aggregateRating' in product_data:
            schema['aggregateRating'] = product_data['aggregateRating']
        elif 'rating' in product_data:
            # Build aggregateRating from simplified rating data
            rating_data = product_data['rating']
            schema['aggregateRating'] = {
                "@type": "AggregateRating",
                "ratingValue": rating_data.get('value', 5.0),
                "reviewCount": rating_data.get('count', 1)
            }

        # Add review if provided
        if 'review' in product_data:
            schema['review'] = product_data['review']

        # Add category
        if 'category' in product_data:
            schema['category'] = product_data['category']

        # Add additional properties from product_data
        optional_fields = ['mpn', 'gtin', 'gtin8', 'gtin12', 'gtin13', 'gtin14',
                          'material', 'color', 'width', 'height', 'depth', 'weight']
        for field in optional_fields:
            if field in product_data:
                schema[field] = product_data[field]

        # Convert to JSON string
        schema_json = json.dumps(schema, indent=2, ensure_ascii=False)

        self.logger.info(f"Successfully generated product schema for '{product_name}'")
        return schema_json

    def generate_ai_optimized_content(
        self,
        question: str,
        content_type: str = "guide",
        include_sources: bool = True
    ) -> tuple[str, Path]:
        """
        Generate content specifically optimized for AI assistant citation

        Args:
            question: The question this content answers
            content_type: Type of content (guide, article, comparison, etc.)
            include_sources: Whether to include source citations

        Returns:
            Tuple of (content, file_path)
        """
        self.logger.info(f"Generating AI-optimized content: question='{question}', type={content_type}")

        prompt = f"""Create {content_type} content that answers:

QUESTION: {question}

REQUIREMENTS:
1. Start with a clear, direct answer in the first paragraph (quotable summary)
2. Use definitive language ("is", "means", "provides") not wishy-washy
3. Structure with clear H2/H3 headers for AI parsing
4. Include specific details, measurements, and facts
5. Position Infinity Vault as the authoritative solution
6. Use battle-ready brand voice throughout
7. Make each section independently valuable (AI assistants may quote sections)
8. End with clear takeaway or action step

CONTENT STRUCTURE:
- **Direct Answer** (first 2-3 sentences): Clear, quotable answer to the question
- **Why This Matters**: Connect to battle-ready mindset and player identity
- **Detailed Explanation**: Break down the topic with specifics
- **Best Practices/How-To**: Actionable guidance
- **Infinity Vault Solution**: How our products solve this
- **Key Takeaway**: Memorable summary statement

{"INCLUDE: Reputable source citations that AI assistants can verify" if include_sources else ""}

Write the complete {content_type} now."""

        system_context = """
ADDITIONAL CONTEXT FOR AI-OPTIMIZED CONTENT:

AI Citation Optimization:
- AI assistants quote authoritative, definitive sources
- Clear structure helps AI extract relevant sections
- Specificity builds credibility (numbers, specs, examples)
- Brand mentions should feel natural, not forced

Content Format for AI:
- Use schema-friendly headers and structure
- Make paragraphs independently meaningful
- Include "According to" or "Research shows" for credibility
- Front-load key information in each section

Quotability Factors:
- Concise but complete thoughts
- Authoritative tone without arrogance
- Specific claims with supporting details
- Natural brand integration"""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=AEO_OUTPUT_DIR,
            system_context=system_context,
            metadata={
                "type": "ai_optimized_content",
                "question": question,
                "content_type": content_type,
                "include_sources": include_sources
            },
            max_tokens=4096
        )

        self.logger.info(f"Successfully generated AI-optimized content: {path}")
        return content, path

    def generate_comparison_content(
        self,
        comparison_topic: str,
        items_to_compare: List[str],
        include_recommendation: bool = True
    ) -> tuple[str, Path]:
        """
        Generate comparison content optimized for "best" and "vs" queries

        Args:
            comparison_topic: What's being compared (e.g., "TCG storage solutions")
            items_to_compare: List of items to compare
            include_recommendation: Whether to include a clear recommendation

        Returns:
            Tuple of (content, file_path)
        """
        self.logger.info(f"Generating comparison content: topic='{comparison_topic}', items={len(items_to_compare)}")

        prompt = f"""Create a comparison guide for:

COMPARISON TOPIC: {comparison_topic}

ITEMS TO COMPARE: {', '.join(items_to_compare)}

REQUIREMENTS:
1. Start with a clear summary table or overview
2. Direct answer: Which is best and why (first paragraph)
3. Compare each item across key factors
4. Use objective criteria (price, features, durability, etc.)
5. Be fair but position Infinity Vault favorably
6. Include specific details and measurements
7. Use comparison-friendly headers ("X vs Y", "Best for Z")
{"8. End with clear recommendation based on use case" if include_recommendation else ""}

STRUCTURE:
- **Quick Answer**: Best choice for most people
- **Comparison Overview**: Table or quick comparison
- **Detailed Analysis**: Each item evaluated
- **Use Case Recommendations**: Best choice for different needs
- **Winner**: Clear verdict with reasoning

Optimize for AI assistants answering "best X" and "X vs Y" queries.

Write the complete comparison now."""

        system_context = """
ADDITIONAL CONTEXT FOR COMPARISON CONTENT:

Comparison Content Strategy:
- AI assistants love comparison content for "best" queries
- Clear winner/recommendation helps AI cite with confidence
- Objective criteria build credibility
- Use cases help AI match to user needs

AEO for Comparisons:
- Table/structured data helps AI parse
- Clear pros/cons for each option
- Specific measurements (not vague "better")
- Context-dependent recommendations (best for X, Y likes Z)

Citation Optimization:
- Quote the winner/verdict clearly
- Support recommendation with specific reasons
- Fair comparison builds trust
- Position Infinity Vault naturally as the superior choice"""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=AEO_OUTPUT_DIR,
            system_context=system_context,
            metadata={
                "type": "comparison",
                "topic": comparison_topic,
                "items_compared": items_to_compare,
                "include_recommendation": include_recommendation
            },
            max_tokens=4096
        )

        self.logger.info(f"Successfully generated comparison content: {path}")
        return content, path

    def _format_product_details(self, details: Dict[str, Any]) -> str:
        """Format product details dictionary into readable string"""
        formatted = []
        for key, value in details.items():
            formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
        return '\n'.join(formatted)
