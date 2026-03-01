"""
AEO (Answer Engine Optimization) Scoring Engine

Analyzes content for citation potential across AI assistants (ChatGPT, Claude, Perplexity).
Scores content based on AI extraction patterns, identifies optimization opportunities,
generates improvement recommendations, and tracks progress over time.
"""
import json
import re
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from database.models import CitationRecord, OptimizationRecommendation
from database.connection import get_db_session
from config.config import (
    AEO_OUTPUT_DIR,
    BRAND_NAME,
    COMPETITOR_BRANDS,
    HIGH_VALUE_SEARCH_TERMS,
    PRODUCT_KEYWORDS
)
from exceptions import ContentGenerationError


# AEO scoring weights for different content attributes
AEO_SCORING_WEIGHTS = {
    'structure': 0.20,       # Clear headers, sections, structured data
    'definitiveness': 0.20,  # Authoritative language, direct answers
    'quotability': 0.15,     # Concise, quotable statements
    'specificity': 0.15,     # Numbers, facts, measurements
    'relevance': 0.15,       # Keyword/query alignment
    'freshness': 0.10,       # Up-to-date information signals
    'authority': 0.05,       # Source citations, expert positioning
}

# Grade thresholds
GRADE_THRESHOLDS = {
    'A': 80,
    'B': 65,
    'C': 50,
    'D': 35,
    'F': 0,
}


class AEOAnalyzer(BaseAgent):
    """Agent specialized in scoring and analyzing content for AEO optimization"""

    def __init__(self):
        """
        Initialize the AEO Analyzer

        Raises:
            AgentInitializationError: If agent initialization fails
        """
        super().__init__(agent_name="aeo_analyzer")
        self.logger.info("AEO Analyzer initialized")

    def analyze_content(
        self,
        content: str,
        target_queries: Optional[List[str]] = None,
        content_url: Optional[str] = None,
        content_type: str = "article",
    ) -> Dict[str, Any]:
        """
        Analyze content for AEO citation potential and generate a comprehensive score

        Performs multi-dimensional analysis of content to assess how likely AI assistants
        are to cite it in responses. Evaluates structure, definitiveness, quotability,
        specificity, relevance, freshness, and authority signals.

        Args:
            content: The content text to analyze
            target_queries: Optional list of queries this content should answer
            content_url: Optional URL where the content is published
            content_type: Type of content (article, faq, guide, comparison)

        Returns:
            Dictionary containing:
                - overall_score: 0-100 overall AEO score
                - grade: Letter grade (A-F)
                - component_scores: Individual dimension scores
                - strengths: List of content strengths
                - weaknesses: List of areas needing improvement
                - recommendations: Actionable improvement suggestions
                - query_alignment: How well content matches target queries
                - metadata: Analysis metadata (timestamp, content_type, etc.)

        Raises:
            ValueError: If content is empty
            ContentGenerationError: For unexpected analysis errors
        """
        if not content or not content.strip():
            raise ValueError("Content parameter is required and cannot be empty")

        self.logger.info(
            f"Analyzing content for AEO potential: type={content_type}, "
            f"length={len(content)} chars, target_queries={len(target_queries or [])}"
        )

        try:
            # Run individual scoring dimensions
            structure_score = self._score_structure(content)
            definitiveness_score = self._score_definitiveness(content)
            quotability_score = self._score_quotability(content)
            specificity_score = self._score_specificity(content)
            relevance_score = self._score_relevance(content, target_queries)
            freshness_score = self._score_freshness(content)
            authority_score = self._score_authority(content)

            component_scores = {
                'structure': {
                    'score': structure_score['score'],
                    'weight': AEO_SCORING_WEIGHTS['structure'],
                    'details': structure_score['details'],
                },
                'definitiveness': {
                    'score': definitiveness_score['score'],
                    'weight': AEO_SCORING_WEIGHTS['definitiveness'],
                    'details': definitiveness_score['details'],
                },
                'quotability': {
                    'score': quotability_score['score'],
                    'weight': AEO_SCORING_WEIGHTS['quotability'],
                    'details': quotability_score['details'],
                },
                'specificity': {
                    'score': specificity_score['score'],
                    'weight': AEO_SCORING_WEIGHTS['specificity'],
                    'details': specificity_score['details'],
                },
                'relevance': {
                    'score': relevance_score['score'],
                    'weight': AEO_SCORING_WEIGHTS['relevance'],
                    'details': relevance_score['details'],
                },
                'freshness': {
                    'score': freshness_score['score'],
                    'weight': AEO_SCORING_WEIGHTS['freshness'],
                    'details': freshness_score['details'],
                },
                'authority': {
                    'score': authority_score['score'],
                    'weight': AEO_SCORING_WEIGHTS['authority'],
                    'details': authority_score['details'],
                },
            }

            # Calculate weighted overall score
            overall_score = sum(
                data['score'] * data['weight']
                for data in component_scores.values()
            )

            # Determine grade
            grade = self._calculate_grade(overall_score)

            # Identify strengths and weaknesses
            strengths = []
            weaknesses = []
            for dimension, data in component_scores.items():
                if data['score'] >= 75:
                    strengths.append(f"{dimension.title()}: {data['details']}")
                elif data['score'] < 50:
                    weaknesses.append(f"{dimension.title()}: {data['details']}")

            # Generate recommendations based on weakest areas
            recommendations = self._generate_content_recommendations(
                component_scores, content_type
            )

            # Assess query alignment if target queries provided
            query_alignment = None
            if target_queries:
                query_alignment = self._assess_query_alignment(content, target_queries)

            result = {
                'overall_score': round(overall_score, 1),
                'grade': grade,
                'component_scores': component_scores,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommendations': recommendations,
                'query_alignment': query_alignment,
                'word_count': len(content.split()),
                'metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'content_type': content_type,
                    'content_url': content_url,
                    'content_length_chars': len(content),
                    'target_queries_count': len(target_queries or []),
                },
            }

            self.logger.info(
                f"AEO analysis complete: score={overall_score:.1f}, grade={grade}, "
                f"strengths={len(strengths)}, weaknesses={len(weaknesses)}"
            )

            return result

        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error analyzing content: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(self.agent_name, "", error_msg)

    def _score_structure(self, content: str) -> Dict[str, Any]:
        """
        Score content structure for AI extraction friendliness

        Checks for clear headers, logical sections, lists, and structured formatting
        that help AI assistants parse and extract information.

        Args:
            content: The content text to analyze

        Returns:
            Dictionary with 'score' (0-100) and 'details' string
        """
        score = 0
        checks = []

        # Check for H2/H3 headers
        h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))

        if h2_count >= 3:
            score += 25
            checks.append(f"{h2_count} H2 headers")
        elif h2_count >= 1:
            score += 15
            checks.append(f"Only {h2_count} H2 headers (need 3+)")

        if h3_count >= 2:
            score += 10
            checks.append(f"{h3_count} H3 subheaders")

        # Check for H1 title
        if re.search(r'^#\s+[^#]', content, re.MULTILINE):
            score += 10
            checks.append("Has H1 title")

        # Check for bullet/numbered lists
        list_items = len(re.findall(r'^[\s]*[-*]\s+', content, re.MULTILINE))
        numbered_items = len(re.findall(r'^[\s]*\d+\.\s+', content, re.MULTILINE))
        total_list_items = list_items + numbered_items

        if total_list_items >= 5:
            score += 20
            checks.append(f"{total_list_items} list items")
        elif total_list_items >= 2:
            score += 10
            checks.append(f"Only {total_list_items} list items")

        # Check for bold/emphasis (key terms highlighted)
        bold_count = len(re.findall(r'\*\*[^*]+\*\*', content))
        if bold_count >= 3:
            score += 10
            checks.append(f"{bold_count} bold terms")

        # Check for reasonable paragraph length (not walls of text)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        if paragraphs:
            avg_paragraph_words = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
            if 30 <= avg_paragraph_words <= 100:
                score += 15
                checks.append("Good paragraph length")
            elif avg_paragraph_words > 150:
                checks.append("Paragraphs too long for AI extraction")
            else:
                score += 5
                checks.append("Short paragraphs")

        # Check for table/comparison structure
        if '|' in content and re.search(r'\|.*\|.*\|', content):
            score += 10
            checks.append("Contains table structure")

        score = min(score, 100)
        detail = "; ".join(checks) if checks else "No structural elements detected"
        return {'score': score, 'details': detail}

    def _score_definitiveness(self, content: str) -> Dict[str, Any]:
        """
        Score content for definitive, authoritative language that AI assistants prefer

        AI assistants prefer citing sources that provide clear, direct answers rather
        than hedging or uncertain language.

        Args:
            content: The content text to analyze

        Returns:
            Dictionary with 'score' (0-100) and 'details' string
        """
        content_lower = content.lower()
        word_count = len(content.split())

        # Definitive language patterns
        definitive_patterns = [
            r'\bis\b', r'\bare\b', r'\bmeans\b', r'\bprovides\b', r'\bdelivers\b',
            r'\bensures\b', r'\bguarantees\b', r'\boffers\b', r'\brepresents\b',
            r'\bthe best\b', r'\bthe most\b', r'\bspecifically\b', r'\bdefinitely\b',
            r'\bresearch shows\b', r'\bstudies confirm\b', r'\bdata indicates\b',
            r'\baccording to\b', r'\bexperts recommend\b',
        ]

        # Uncertain/hedging language (penalize)
        uncertain_patterns = [
            r'\bmight\b', r'\bcould\b', r'\bperhaps\b', r'\bpossibly\b',
            r'\bmaybe\b', r'\bsome people think\b', r'\bit depends\b',
            r'\bgenerally speaking\b', r'\bin some cases\b', r'\bkind of\b',
            r'\bsort of\b',
        ]

        # Count definitive phrases
        definitive_count = 0
        for pattern in definitive_patterns:
            definitive_count += len(re.findall(pattern, content_lower))

        # Count uncertain phrases
        uncertain_count = 0
        for pattern in uncertain_patterns:
            uncertain_count += len(re.findall(pattern, content_lower))

        # Calculate ratio per 100 words
        definitive_per_100 = (definitive_count / max(word_count, 1)) * 100
        uncertain_per_100 = (uncertain_count / max(word_count, 1)) * 100

        # Score based on definitiveness ratio
        score = 50  # Base score

        # Reward definitive language
        if definitive_per_100 >= 5:
            score += 30
        elif definitive_per_100 >= 3:
            score += 20
        elif definitive_per_100 >= 1:
            score += 10

        # Penalize uncertain language
        if uncertain_per_100 >= 3:
            score -= 25
        elif uncertain_per_100 >= 1.5:
            score -= 15
        elif uncertain_per_100 >= 0.5:
            score -= 5

        # Check for direct answer at the beginning (first 200 chars)
        first_section = content[:500].lower()
        has_direct_opening = any(
            phrase in first_section
            for phrase in ['is ', 'are ', 'means ', 'the best ', 'the answer']
        )
        if has_direct_opening:
            score += 20

        score = max(0, min(score, 100))

        checks = []
        checks.append(f"{definitive_count} definitive phrases")
        if uncertain_count > 0:
            checks.append(f"{uncertain_count} uncertain phrases")
        if has_direct_opening:
            checks.append("Direct opening answer")

        return {'score': score, 'details': "; ".join(checks)}

    def _score_quotability(self, content: str) -> Dict[str, Any]:
        """
        Score content for quotability - how easily AI assistants can extract
        and quote key statements.

        Args:
            content: The content text to analyze

        Returns:
            Dictionary with 'score' (0-100) and 'details' string
        """
        score = 0
        checks = []

        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

        if not sentences:
            return {'score': 0, 'details': 'No analyzable sentences'}

        # Check for ideal sentence length for quoting (15-40 words)
        quotable_sentences = [
            s for s in sentences
            if 10 <= len(s.split()) <= 40
        ]
        quotable_ratio = len(quotable_sentences) / len(sentences)

        if quotable_ratio >= 0.6:
            score += 35
            checks.append(f"{len(quotable_sentences)}/{len(sentences)} quotable-length sentences")
        elif quotable_ratio >= 0.3:
            score += 20
            checks.append(f"Some quotable sentences ({quotable_ratio:.0%})")

        # Check for self-contained statements (don't start with "However", "Also", "But")
        self_contained = [
            s for s in quotable_sentences
            if not re.match(r'^(however|also|but|and|or|yet|furthermore|moreover|additionally)\b', s.lower())
        ]
        if len(self_contained) >= 3:
            score += 20
            checks.append(f"{len(self_contained)} self-contained quotable statements")

        # Check for key takeaway/summary patterns
        summary_patterns = [
            r'in summary', r'key takeaway', r'bottom line', r'the answer is',
            r'most importantly', r'in conclusion', r'the result is',
        ]
        has_summary = any(
            re.search(pattern, content.lower())
            for pattern in summary_patterns
        )
        if has_summary:
            score += 15
            checks.append("Has summary/takeaway statement")

        # Check for bold statements that stand out
        bold_statements = re.findall(r'\*\*([^*]+)\*\*', content)
        quotable_bold = [b for b in bold_statements if len(b.split()) >= 3]
        if quotable_bold:
            score += 15
            checks.append(f"{len(quotable_bold)} bold key statements")

        # Check opening paragraph directness
        first_paragraph = content.split('\n\n')[0] if '\n\n' in content else content[:300]
        first_words = len(first_paragraph.split())
        if first_words <= 60:
            score += 15
            checks.append("Concise opening paragraph")

        score = min(score, 100)
        return {'score': score, 'details': "; ".join(checks) if checks else "Limited quotability"}

    def _score_specificity(self, content: str) -> Dict[str, Any]:
        """
        Score content for specificity - concrete details, numbers, and facts
        that make content more credible and citable.

        Args:
            content: The content text to analyze

        Returns:
            Dictionary with 'score' (0-100) and 'details' string
        """
        score = 0
        checks = []

        # Check for numbers/statistics
        numbers = re.findall(r'\b\d+(?:\.\d+)?(?:\s*%|\s*percent|\s*x\b|\s*times)', content, re.IGNORECASE)
        plain_numbers = re.findall(r'\b\d{2,}\b', content)
        total_numbers = len(numbers) + len(plain_numbers)

        if total_numbers >= 10:
            score += 30
            checks.append(f"{total_numbers} numeric references")
        elif total_numbers >= 5:
            score += 20
            checks.append(f"{total_numbers} numeric references")
        elif total_numbers >= 2:
            score += 10
            checks.append(f"Only {total_numbers} numeric references")

        # Check for specific measurements/dimensions
        measurements = re.findall(
            r'\b\d+(?:\.\d+)?\s*(?:inches?|in\b|cm|mm|oz|lbs?|grams?|ml|")',
            content, re.IGNORECASE
        )
        if measurements:
            score += 15
            checks.append(f"{len(measurements)} specific measurements")

        # Check for brand/product names (specificity signal)
        brand_mentions = content.lower().count(BRAND_NAME.lower())
        if brand_mentions >= 2:
            score += 10
            checks.append(f"{brand_mentions} brand mentions")

        # Check for specific product names or model numbers
        product_mention_count = 0
        for keyword in PRODUCT_KEYWORDS:
            if keyword.lower() in content.lower():
                product_mention_count += 1
        if product_mention_count >= 3:
            score += 15
            checks.append(f"{product_mention_count} product keywords")
        elif product_mention_count >= 1:
            score += 8
            checks.append(f"{product_mention_count} product keywords")

        # Check for comparison words (vs, compared to, better than)
        comparison_patterns = [
            r'\bvs\.?\b', r'\bversus\b', r'\bcompared to\b', r'\bbetter than\b',
            r'\bunlike\b', r'\bin contrast\b',
        ]
        comparison_count = sum(
            len(re.findall(pattern, content, re.IGNORECASE))
            for pattern in comparison_patterns
        )
        if comparison_count >= 2:
            score += 15
            checks.append(f"{comparison_count} comparisons")

        # Check for specific examples
        example_patterns = [r'\bfor example\b', r'\bsuch as\b', r'\bincluding\b', r'\blike\b']
        example_count = sum(
            len(re.findall(pattern, content, re.IGNORECASE))
            for pattern in example_patterns
        )
        if example_count >= 3:
            score += 15
            checks.append(f"{example_count} specific examples")
        elif example_count >= 1:
            score += 8

        score = min(score, 100)
        return {'score': score, 'details': "; ".join(checks) if checks else "Lacks specific details"}

    def _score_relevance(
        self, content: str, target_queries: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Score content relevance to target queries and high-value search terms

        Args:
            content: The content text to analyze
            target_queries: Optional list of target queries

        Returns:
            Dictionary with 'score' (0-100) and 'details' string
        """
        content_lower = content.lower()
        score = 0
        checks = []

        # Check alignment with high-value search terms
        matched_terms = []
        for term in HIGH_VALUE_SEARCH_TERMS:
            # Check for partial keyword matches (individual words from the term)
            term_words = term.lower().split()
            matching_words = sum(1 for w in term_words if w in content_lower)
            if matching_words >= len(term_words) * 0.6:
                matched_terms.append(term)

        if matched_terms:
            term_score = min(len(matched_terms) * 8, 40)
            score += term_score
            checks.append(f"Matches {len(matched_terms)} high-value search terms")

        # Check target query alignment if provided
        if target_queries:
            aligned_queries = 0
            for query in target_queries:
                query_words = query.lower().split()
                matching_words = sum(1 for w in query_words if w in content_lower)
                if matching_words >= len(query_words) * 0.5:
                    aligned_queries += 1

            if aligned_queries > 0:
                query_score = min(aligned_queries * 15, 40)
                score += query_score
                checks.append(f"Aligns with {aligned_queries}/{len(target_queries)} target queries")
        else:
            # No target queries provided; give partial credit for general keyword coverage
            score += 20
            checks.append("No target queries provided for alignment check")

        # Check for question-answer patterns (FAQ style helps AI extraction)
        qa_patterns = len(re.findall(r'\?[\s\n]', content))
        if qa_patterns >= 3:
            score += 20
            checks.append(f"{qa_patterns} Q&A patterns")
        elif qa_patterns >= 1:
            score += 10

        score = min(score, 100)
        return {'score': score, 'details': "; ".join(checks) if checks else "Low relevance to target queries"}

    def _score_freshness(self, content: str) -> Dict[str, Any]:
        """
        Score content for freshness signals (dates, current references)

        AI assistants prefer citing up-to-date information.

        Args:
            content: The content text to analyze

        Returns:
            Dictionary with 'score' (0-100) and 'details' string
        """
        score = 50  # Base score for any content
        checks = []

        # Check for year references
        current_year = datetime.utcnow().year
        recent_years = [str(current_year), str(current_year - 1)]

        has_current_year = any(year in content for year in recent_years)
        if has_current_year:
            score += 25
            checks.append(f"References {current_year} or {current_year - 1}")

        # Check for "updated" or "latest" signals
        freshness_signals = [
            r'\bupdated\b', r'\blatest\b', r'\bcurrent\b', r'\bnew\b',
            r'\brecent(?:ly)?\b', r'\btoday\b', r'\bthis year\b',
        ]
        signal_count = sum(
            len(re.findall(pattern, content, re.IGNORECASE))
            for pattern in freshness_signals
        )
        if signal_count >= 3:
            score += 20
            checks.append(f"{signal_count} freshness signals")
        elif signal_count >= 1:
            score += 10
            checks.append(f"{signal_count} freshness signals")

        # Check for outdated year references
        old_years = [str(y) for y in range(2018, current_year - 1)]
        has_old_references = any(year in content for year in old_years)
        if has_old_references and not has_current_year:
            score -= 15
            checks.append("Contains outdated year references without current updates")

        score = max(0, min(score, 100))
        return {'score': score, 'details': "; ".join(checks) if checks else "No freshness signals detected"}

    def _score_authority(self, content: str) -> Dict[str, Any]:
        """
        Score content for authority signals (expert positioning, source citations)

        Args:
            content: The content text to analyze

        Returns:
            Dictionary with 'score' (0-100) and 'details' string
        """
        content_lower = content.lower()
        score = 0
        checks = []

        # Check for expert positioning phrases
        expert_patterns = [
            r'\bexperts?\b', r'\bresearch\b', r'\bstudies?\b', r'\bdata\b',
            r'\baccording to\b', r'\bproven\b', r'\btested\b', r'\bcertified\b',
            r'\bindustry\b', r'\bprofessional\b',
        ]
        expert_count = sum(
            len(re.findall(pattern, content_lower))
            for pattern in expert_patterns
        )
        if expert_count >= 5:
            score += 30
            checks.append(f"{expert_count} authority signals")
        elif expert_count >= 2:
            score += 20
            checks.append(f"{expert_count} authority signals")
        elif expert_count >= 1:
            score += 10

        # Check for source citations or references
        citation_patterns = [
            r'source:', r'\[.*?\]\(.*?\)', r'https?://',
            r'according to', r'referenced by', r'as noted by',
        ]
        citation_count = sum(
            len(re.findall(pattern, content_lower))
            for pattern in citation_patterns
        )
        if citation_count >= 3:
            score += 25
            checks.append(f"{citation_count} source references")
        elif citation_count >= 1:
            score += 15
            checks.append(f"{citation_count} source references")

        # Check for brand authority positioning
        authority_phrases = [
            r'we\s+(?:have|provide|offer|deliver|ensure)',
            r'our\s+(?:team|experts?|experience|testing)',
            r'years?\s+of\s+experience',
        ]
        has_brand_authority = any(
            re.search(pattern, content_lower) for pattern in authority_phrases
        )
        if has_brand_authority:
            score += 20
            checks.append("Brand authority positioning present")

        # Check for social proof
        social_patterns = [
            r'\bcustomer\b', r'\breview\b', r'\brating\b', r'\btestimonial\b',
            r'\bfeedback\b', r'\btrusted\b', r'\brecommend\b',
        ]
        social_count = sum(
            len(re.findall(pattern, content_lower))
            for pattern in social_patterns
        )
        if social_count >= 3:
            score += 25
            checks.append(f"{social_count} social proof signals")
        elif social_count >= 1:
            score += 10

        score = min(score, 100)
        return {'score': score, 'details': "; ".join(checks) if checks else "No authority signals"}

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from numeric score"""
        for grade, threshold in GRADE_THRESHOLDS.items():
            if score >= threshold:
                return grade
        return 'F'

    def _generate_content_recommendations(
        self,
        component_scores: Dict[str, Dict],
        content_type: str
    ) -> List[Dict[str, str]]:
        """
        Generate actionable recommendations based on component scores

        Args:
            component_scores: Dictionary of component score data
            content_type: Type of content being analyzed

        Returns:
            List of recommendation dictionaries with 'area', 'priority', and 'action'
        """
        recommendations = []

        # Sort components by score (lowest first) to prioritize improvements
        sorted_components = sorted(
            component_scores.items(),
            key=lambda x: x[1]['score']
        )

        recommendation_map = {
            'structure': {
                'low': 'Add clear H2/H3 headers, bullet lists, and structured sections to improve AI parsing',
                'medium': 'Consider adding tables, comparison sections, or FAQ formatting for better extraction',
            },
            'definitiveness': {
                'low': 'Replace hedging language (might, could, perhaps) with definitive statements (is, provides, ensures)',
                'medium': 'Front-load direct answers in the first paragraph of each section',
            },
            'quotability': {
                'low': 'Create concise, self-contained statements (15-40 words) that AI can easily quote',
                'medium': 'Add bold key takeaways and a summary section with quotable conclusions',
            },
            'specificity': {
                'low': 'Add specific numbers, measurements, statistics, and concrete examples throughout',
                'medium': 'Include product comparisons with specific features and direct brand mentions',
            },
            'relevance': {
                'low': 'Align content with high-value search queries that users ask AI assistants',
                'medium': 'Add FAQ-style question-answer patterns matching common user queries',
            },
            'freshness': {
                'low': 'Add current year references and update terminology to signal fresh content',
                'medium': 'Include "updated" or "latest" markers and remove outdated date references',
            },
            'authority': {
                'low': 'Add expert positioning, source citations, and social proof elements',
                'medium': 'Include brand authority statements and customer testimonials',
            },
        }

        for dimension, data in sorted_components:
            if data['score'] < 50:
                priority = 'high'
                action = recommendation_map.get(dimension, {}).get('low', f'Improve {dimension} scoring')
            elif data['score'] < 75:
                priority = 'medium'
                action = recommendation_map.get(dimension, {}).get('medium', f'Enhance {dimension} scoring')
            else:
                continue

            recommendations.append({
                'area': dimension,
                'priority': priority,
                'current_score': round(data['score'], 1),
                'action': action,
            })

        return recommendations

    def _assess_query_alignment(
        self, content: str, target_queries: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Assess how well content aligns with specific target queries

        Args:
            content: The content text
            target_queries: List of queries to check alignment against

        Returns:
            List of dictionaries with query alignment details
        """
        content_lower = content.lower()
        results = []

        for query in target_queries:
            query_words = query.lower().split()
            total_words = len(query_words)

            # Count how many query words appear in content
            matched_words = [w for w in query_words if w in content_lower]
            match_ratio = len(matched_words) / max(total_words, 1)

            # Check if content contains the exact query phrase
            exact_match = query.lower() in content_lower

            # Determine alignment level
            if exact_match:
                alignment = 'strong'
            elif match_ratio >= 0.7:
                alignment = 'good'
            elif match_ratio >= 0.4:
                alignment = 'partial'
            else:
                alignment = 'weak'

            results.append({
                'query': query,
                'alignment': alignment,
                'match_ratio': round(match_ratio, 2),
                'matched_words': matched_words,
                'exact_match': exact_match,
            })

        return results

    def analyze_and_save(
        self,
        content: str,
        target_queries: Optional[List[str]] = None,
        content_url: Optional[str] = None,
        content_type: str = "article",
        filename: Optional[str] = None,
    ) -> tuple[Dict[str, Any], Path]:
        """
        Analyze content and save results to file

        Args:
            content: Content to analyze
            target_queries: Optional target queries
            content_url: Optional content URL
            content_type: Type of content
            filename: Optional output filename

        Returns:
            Tuple of (analysis_result, output_path)
        """
        self.logger.info("Running analyze_and_save workflow")

        analysis = self.analyze_content(
            content=content,
            target_queries=target_queries,
            content_url=content_url,
            content_type=content_type,
        )

        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"aeo_analysis_{timestamp}.json"

        output_path = AEO_OUTPUT_DIR / filename
        AEO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(analysis, indent=2))

        self.logger.info(f"AEO analysis saved to: {output_path}")
        return analysis, output_path

    def batch_analyze(
        self,
        content_items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze multiple content items and generate a summary report

        Args:
            content_items: List of dicts with 'content', optional 'target_queries',
                          'content_url', 'content_type', and 'title' keys

        Returns:
            Dictionary with individual results and aggregate summary
        """
        if not content_items:
            raise ValueError("content_items cannot be empty")

        self.logger.info(f"Batch analyzing {len(content_items)} content items")

        results = []
        total_score = 0

        for idx, item in enumerate(content_items):
            content = item.get('content', '')
            if not content:
                self.logger.warning(f"Skipping item {idx}: empty content")
                continue

            analysis = self.analyze_content(
                content=content,
                target_queries=item.get('target_queries'),
                content_url=item.get('content_url'),
                content_type=item.get('content_type', 'article'),
            )

            results.append({
                'title': item.get('title', f'Content {idx + 1}'),
                'analysis': analysis,
            })
            total_score += analysis['overall_score']

        avg_score = total_score / max(len(results), 1)
        avg_grade = self._calculate_grade(avg_score)

        # Aggregate common weaknesses
        weakness_counts = {}
        for result in results:
            for rec in result['analysis']['recommendations']:
                area = rec['area']
                weakness_counts[area] = weakness_counts.get(area, 0) + 1

        common_weaknesses = sorted(
            weakness_counts.items(), key=lambda x: x[1], reverse=True
        )

        summary = {
            'total_items': len(results),
            'average_score': round(avg_score, 1),
            'average_grade': avg_grade,
            'score_distribution': {
                'A': sum(1 for r in results if r['analysis']['grade'] == 'A'),
                'B': sum(1 for r in results if r['analysis']['grade'] == 'B'),
                'C': sum(1 for r in results if r['analysis']['grade'] == 'C'),
                'D': sum(1 for r in results if r['analysis']['grade'] == 'D'),
                'F': sum(1 for r in results if r['analysis']['grade'] == 'F'),
            },
            'common_weaknesses': [
                {'area': area, 'frequency': count}
                for area, count in common_weaknesses[:5]
            ],
        }

        self.logger.info(
            f"Batch analysis complete: {len(results)} items, "
            f"avg_score={avg_score:.1f}, avg_grade={avg_grade}"
        )

        return {
            'results': results,
            'summary': summary,
        }

    def track_progress(
        self,
        content_url: str,
        current_score: float,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Track AEO score progress over time for a specific content URL

        Stores the current score and compares against historical scores to show
        improvement trends.

        Args:
            content_url: URL of the content being tracked
            current_score: The current AEO score
            db_session: Optional database session

        Returns:
            Dictionary with progress tracking data including trend direction
        """
        self.logger.info(f"Tracking AEO progress for: {content_url}")

        session_provided = db_session is not None
        if not session_provided:
            db_session = get_db_session()

        try:
            # Query recent optimization recommendations for this URL
            recent_recs = db_session.query(OptimizationRecommendation).filter(
                OptimizationRecommendation.recommendation_metadata.contains(content_url),
            ).order_by(
                OptimizationRecommendation.created_at.desc()
            ).limit(10).all()

            # Build historical scores from recommendations metadata
            historical_scores = []
            for rec in recent_recs:
                if rec.recommendation_metadata:
                    try:
                        meta = json.loads(rec.recommendation_metadata) if isinstance(
                            rec.recommendation_metadata, str
                        ) else rec.recommendation_metadata
                        if 'aeo_score' in meta:
                            historical_scores.append({
                                'score': meta['aeo_score'],
                                'date': rec.created_at.isoformat() if rec.created_at else None,
                            })
                    except (json.JSONDecodeError, TypeError):
                        pass

            # Determine trend
            if len(historical_scores) >= 2:
                latest_historical = historical_scores[0]['score']
                if current_score > latest_historical:
                    trend = 'improving'
                    change = current_score - latest_historical
                elif current_score < latest_historical:
                    trend = 'declining'
                    change = current_score - latest_historical
                else:
                    trend = 'stable'
                    change = 0
            else:
                trend = 'new'
                change = 0

            # Save current score as a new recommendation tracking entry
            new_rec = OptimizationRecommendation(
                recommendation_type='content',
                title=f'AEO Score Tracking: {current_score:.1f}',
                description=f'AEO score tracking for {content_url}',
                priority='medium',
                status='implemented',
                expected_impact=int(current_score),
                recommendation_metadata=json.dumps({
                    'aeo_score': current_score,
                    'content_url': content_url,
                    'tracked_at': datetime.utcnow().isoformat(),
                }),
            )
            db_session.add(new_rec)
            db_session.commit()

            result = {
                'content_url': content_url,
                'current_score': current_score,
                'trend': trend,
                'change': round(change, 1),
                'historical_scores': historical_scores[:5],
                'total_tracked': len(historical_scores) + 1,
            }

            self.logger.info(
                f"Progress tracked: score={current_score}, trend={trend}, change={change:+.1f}"
            )

            return result

        except Exception as e:
            db_session.rollback()
            error_msg = f"Error tracking AEO progress: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(self.agent_name, "", error_msg)

        finally:
            if not session_provided and db_session:
                db_session.close()

    def generate_optimization_report(
        self,
        content: str,
        target_queries: Optional[List[str]] = None,
        content_type: str = "article",
    ) -> tuple[str, Path]:
        """
        Generate a detailed AEO optimization report using AI analysis

        Uses Claude to perform deeper qualitative analysis beyond the rule-based scoring,
        providing natural language recommendations tailored to the specific content.

        Args:
            content: The content to analyze
            target_queries: Optional target queries
            content_type: Type of content

        Returns:
            Tuple of (report_content, file_path)
        """
        self.logger.info("Generating AI-powered AEO optimization report")

        # First run the automated analysis
        analysis = self.analyze_content(
            content=content,
            target_queries=target_queries,
            content_type=content_type,
        )

        prompt = f"""Analyze this content for Answer Engine Optimization (AEO) and provide
a detailed optimization report.

CONTENT TO ANALYZE:
{content[:3000]}

AUTOMATED ANALYSIS RESULTS:
- Overall Score: {analysis['overall_score']}/100 (Grade: {analysis['grade']})
- Structure Score: {analysis['component_scores']['structure']['score']}/100
- Definitiveness Score: {analysis['component_scores']['definitiveness']['score']}/100
- Quotability Score: {analysis['component_scores']['quotability']['score']}/100
- Specificity Score: {analysis['component_scores']['specificity']['score']}/100
- Relevance Score: {analysis['component_scores']['relevance']['score']}/100
- Freshness Score: {analysis['component_scores']['freshness']['score']}/100
- Authority Score: {analysis['component_scores']['authority']['score']}/100

TARGET QUERIES: {', '.join(target_queries) if target_queries else 'Not specified'}

PROVIDE:
1. **Executive Summary**: 2-3 sentence overview of AEO readiness
2. **Top 3 Strengths**: What this content does well for AI citation
3. **Top 3 Improvements**: Most impactful changes to increase citations
4. **Specific Rewrites**: Provide 2-3 example sentence rewrites that would improve
   definitiveness and quotability
5. **Query Gap Analysis**: Which target queries are not well-addressed
6. **Action Plan**: Prioritized list of 5 specific actions to improve the AEO score

Format as a clean, actionable report in markdown."""

        system_context = """You are an AEO (Answer Engine Optimization) expert.
Your job is to analyze content and provide actionable recommendations for improving
how often AI assistants cite this content in their responses.

Key principles:
- AI assistants prefer definitive, authoritative content over hedging language
- Clear structure with headers helps AI extract and cite specific sections
- Quotable, self-contained statements are more likely to be cited
- Specific numbers and facts build credibility
- Content that directly answers common user queries gets cited more
- Fresh, current content is preferred over outdated information"""

        report_content, report_path = self.generate_and_save(
            prompt=prompt,
            output_dir=AEO_OUTPUT_DIR,
            system_context=system_context,
            filename=f"aeo_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            metadata={
                'type': 'aeo_optimization_report',
                'automated_score': analysis['overall_score'],
                'automated_grade': analysis['grade'],
                'content_type': content_type,
                'target_queries': target_queries,
            },
            max_tokens=4096,
        )

        self.logger.info(f"AEO optimization report saved to: {report_path}")
        return report_content, report_path
