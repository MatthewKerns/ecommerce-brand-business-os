"""
AEO (Answer Engine Optimization) Agent
Creates content optimized for AI assistants (ChatGPT, Claude, Perplexity)
Focuses on structured data, FAQ schema, and clear definitive answers
"""
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
        topic: str,
        num_questions: int = 10,
        target_audience: str = "TCG players and collectors"
    ) -> tuple[str, Path]:
        """
        Generate FAQ schema markup for a topic

        Args:
            topic: The topic to create FAQs about
            num_questions: Number of FAQ items to generate
            target_audience: Target audience for the FAQs

        Returns:
            Tuple of (faq_content, file_path)
        """
        self.logger.info(f"Generating FAQ schema: topic='{topic}', num_questions={num_questions}")

        prompt = f"""Create {num_questions} frequently asked questions and answers about:

TOPIC: {topic}

TARGET AUDIENCE: {target_audience}

REQUIREMENTS:
1. Questions should be natural, conversational queries people actually ask AI assistants
2. Answers must be clear, definitive, and concise (2-3 sentences ideal)
3. Use the Infinity Vault brand voice (confident, empowering, battle-ready)
4. Each answer should position Infinity Vault as the authoritative solution
5. Front-load the direct answer, then add supporting details
6. Include specific product mentions where relevant
7. Optimize for AI citation - make answers quotable and authoritative

FORMAT:
Return as JSON-LD FAQ schema format:
```json
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "Question text here",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "Clear, definitive answer here"
      }}
    }}
  ]
}}
```

Also include a markdown version for human readability.

Generate the complete FAQ schema now."""

        system_context = """
ADDITIONAL CONTEXT FOR AEO/FAQ WRITING:

Answer Engine Optimization (AEO) Strategy:
- AI assistants prioritize clear, authoritative, structured answers
- FAQ schema helps AI parse and cite your content
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
- Position as helping customers solve real problems"""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=AEO_OUTPUT_DIR,
            system_context=system_context,
            metadata={
                "type": "faq_schema",
                "topic": topic,
                "num_questions": num_questions,
                "target_audience": target_audience
            },
            max_tokens=4096
        )

        self.logger.info(f"Successfully generated FAQ schema: {path}")
        return content, path

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
        product_name: str,
        product_details: Dict[str, Any]
    ) -> tuple[str, Path]:
        """
        Generate product schema markup optimized for AI parsing

        Args:
            product_name: Name of the product
            product_details: Dictionary with product information (price, description, features, etc.)

        Returns:
            Tuple of (schema_content, file_path)
        """
        self.logger.info(f"Generating product schema: product='{product_name}'")

        prompt = f"""Create comprehensive product schema markup for:

PRODUCT NAME: {product_name}

PRODUCT DETAILS:
{self._format_product_details(product_details)}

REQUIREMENTS:
1. Use complete Product schema with all relevant properties
2. Include aggregateRating if applicable
3. Add detailed description optimized for AI understanding
4. Include all technical specifications
5. Add brand information (Infinity Vault)
6. Include category and use case information
7. Make it easy for AI assistants to understand what this product is and who it's for

FORMAT:
Return as JSON-LD Product schema format with all relevant properties.

Also include recommendations for:
- Key phrases AI assistants should associate with this product
- Questions this product answers
- Use cases to highlight for AI citation

Generate the complete product schema now."""

        system_context = """
ADDITIONAL CONTEXT FOR PRODUCT SCHEMA:

Product Schema Strategy:
- Complete schemas help AI assistants understand products deeply
- Include technical specs AND emotional benefits
- Category and use case help AI match products to queries
- Brand information builds authority

AI Assistant Product Discovery:
- AI assistants look for clear product-problem fit
- Specifications help AI filter and recommend accurately
- Reviews and ratings build trust signals
- Clear categorization helps AI match to user needs"""

        content, path = self.generate_and_save(
            prompt=prompt,
            output_dir=AEO_OUTPUT_DIR,
            system_context=system_context,
            metadata={
                "type": "product_schema",
                "product_name": product_name,
                "product_details": product_details
            }
        )

        self.logger.info(f"Successfully generated product schema: {path}")
        return content, path

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
