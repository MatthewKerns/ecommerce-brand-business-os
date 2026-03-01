"""
AEO Content Checklist
Validates content against Answer Engine Optimization requirements
Ensures content is optimized for AI assistant discovery and citation
"""
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from logging_config import get_logger


class AEOChecklist:
    """
    Validates content against AEO (Answer Engine Optimization) requirements

    Checks content for:
    - Clear, definitive answers
    - Structured headers for AI parsing
    - FAQ-style content
    - Quotable sections
    - Brand mentions
    - Definitive language usage
    - Front-loaded key information
    """

    # AEO requirement weights for scoring
    REQUIREMENT_WEIGHTS = {
        "has_clear_answer": 0.20,
        "has_structured_headers": 0.15,
        "has_faq": 0.15,
        "uses_definitive_language": 0.15,
        "has_brand_mention": 0.10,
        "is_quotable": 0.10,
        "front_loads_answer": 0.10,
        "has_specifics": 0.05
    }

    # Definitive language patterns
    DEFINITIVE_PATTERNS = [
        r'\bis\b',
        r'\bare\b',
        r'\bmeans\b',
        r'\bprovides\b',
        r'\boffers\b',
        r'\bdelivers\b',
        r'\bensures\b',
        r'\nguarantees\b'
    ]

    # Weak/uncertain language patterns (to avoid)
    WEAK_PATTERNS = [
        r'\bmight\b',
        r'\bmaybe\b',
        r'\bcould\b',
        r'\bpossibly\b',
        r'\bperhaps\b',
        r'\bprobably\b',
        r'\bseems?\b',
        r'\bappears?\b'
    ]

    # Brand mentions to check
    BRAND_NAMES = [
        "Infinity Vault",
        "infinity vault",
        "InfinityVault"
    ]

    def __init__(self):
        """Initialize the AEO checklist validator"""
        self.logger = get_logger("aeo_checklist")
        self.logger.info("AEO Checklist initialized")

    def validate_content(
        self,
        content: str,
        content_type: str = "article",
        target_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate content against AEO requirements

        Args:
            content: The content to validate (markdown format)
            content_type: Type of content (article, faq, guide, comparison)
            target_query: Optional target query this content should answer

        Returns:
            Dictionary with validation results:
            {
                "score": float,  # Overall AEO score (0-100)
                "passed": bool,  # Whether content meets minimum requirements
                "checks": dict,  # Individual check results
                "recommendations": list,  # Improvement suggestions
                "metadata": dict  # Validation metadata
            }
        """
        self.logger.info(f"Validating content: type={content_type}, length={len(content)} chars")

        # Run individual validation checks
        checks = {
            "has_clear_answer": self._check_clear_answer(content, target_query),
            "has_structured_headers": self._check_structured_headers(content),
            "has_faq": self._check_faq_format(content),
            "uses_definitive_language": self._check_definitive_language(content),
            "has_brand_mention": self._check_brand_mention(content),
            "is_quotable": self._check_quotability(content),
            "front_loads_answer": self._check_front_loaded(content, target_query),
            "has_specifics": self._check_specifics(content)
        }

        # Calculate overall score
        score = self._calculate_score(checks)

        # Determine if content passes minimum requirements
        passed = self._check_pass_threshold(checks, score)

        # Generate recommendations
        recommendations = self._generate_recommendations(checks, content_type)

        # Build result
        result = {
            "score": score,
            "passed": passed,
            "checks": checks,
            "recommendations": recommendations,
            "metadata": {
                "content_type": content_type,
                "content_length": len(content),
                "target_query": target_query,
                "validated_at": datetime.now().isoformat(),
                "word_count": len(content.split())
            }
        }

        self.logger.info(f"Validation complete: score={score:.1f}, passed={passed}")
        return result

    def _check_clear_answer(self, content: str, target_query: Optional[str]) -> Dict[str, Any]:
        """Check if content has a clear, direct answer"""
        # Extract first paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        if not paragraphs:
            return {"passed": False, "score": 0.0, "reason": "No paragraphs found"}

        first_para = paragraphs[0]

        # Skip headers in first paragraph
        if first_para.startswith('#'):
            if len(paragraphs) > 1:
                first_para = paragraphs[1]
            else:
                return {"passed": False, "score": 0.0, "reason": "Only header found, no content"}

        # Check first paragraph length (should be substantial but not too long)
        word_count = len(first_para.split())
        if word_count < 20:
            return {"passed": False, "score": 0.3, "reason": "First paragraph too short"}

        if word_count > 150:
            return {"passed": False, "score": 0.5, "reason": "First paragraph too long (not direct)"}

        # Check for definitive language in first paragraph
        has_definitive = any(
            re.search(pattern, first_para, re.IGNORECASE)
            for pattern in self.DEFINITIVE_PATTERNS
        )

        if not has_definitive:
            return {"passed": False, "score": 0.6, "reason": "First paragraph lacks definitive language"}

        return {
            "passed": True,
            "score": 1.0,
            "reason": "Clear direct answer in opening",
            "first_paragraph_words": word_count
        }

    def _check_structured_headers(self, content: str) -> Dict[str, Any]:
        """Check for clear header structure for AI parsing"""
        # Find all markdown headers
        h1_headers = re.findall(r'^# .+$', content, re.MULTILINE)
        h2_headers = re.findall(r'^## .+$', content, re.MULTILINE)
        h3_headers = re.findall(r'^### .+$', content, re.MULTILINE)

        total_headers = len(h1_headers) + len(h2_headers) + len(h3_headers)

        if total_headers == 0:
            return {"passed": False, "score": 0.0, "reason": "No headers found"}

        if total_headers < 3:
            return {"passed": False, "score": 0.4, "reason": "Too few headers for good structure"}

        # Check if headers are descriptive (not just single words)
        descriptive_headers = 0
        all_headers = h1_headers + h2_headers + h3_headers

        for header in all_headers:
            # Remove markdown symbols
            header_text = re.sub(r'^#+\s+', '', header)
            if len(header_text.split()) >= 2:
                descriptive_headers += 1

        descriptive_ratio = descriptive_headers / total_headers if total_headers > 0 else 0

        if descriptive_ratio < 0.5:
            return {
                "passed": False,
                "score": 0.6,
                "reason": "Headers not descriptive enough",
                "total_headers": total_headers
            }

        return {
            "passed": True,
            "score": 1.0,
            "reason": "Good header structure",
            "total_headers": total_headers,
            "h1_count": len(h1_headers),
            "h2_count": len(h2_headers),
            "h3_count": len(h3_headers)
        }

    def _check_faq_format(self, content: str) -> Dict[str, Any]:
        """Check for FAQ-style question/answer format"""
        # Look for question patterns
        question_patterns = [
            r'^##\s+.*\?$',  # H2 headers ending with ?
            r'^###\s+.*\?$',  # H3 headers ending with ?
            r'^\*\*.*\?\*\*',  # Bold questions
            r'^Q:',  # Q: format
        ]

        questions_found = 0
        for pattern in question_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            questions_found += len(matches)

        if questions_found == 0:
            return {"passed": False, "score": 0.0, "reason": "No FAQ format detected"}

        if questions_found < 3:
            return {
                "passed": False,
                "score": 0.5,
                "reason": "Some questions found but not enough for FAQ",
                "questions_count": questions_found
            }

        return {
            "passed": True,
            "score": 1.0,
            "reason": "Good FAQ format with multiple Q&As",
            "questions_count": questions_found
        }

    def _check_definitive_language(self, content: str) -> Dict[str, Any]:
        """Check for definitive vs uncertain language"""
        # Count definitive language
        definitive_count = sum(
            len(re.findall(pattern, content, re.IGNORECASE))
            for pattern in self.DEFINITIVE_PATTERNS
        )

        # Count weak language
        weak_count = sum(
            len(re.findall(pattern, content, re.IGNORECASE))
            for pattern in self.WEAK_PATTERNS
        )

        total_words = len(content.split())

        # Calculate ratios per 100 words
        definitive_density = (definitive_count / total_words) * 100 if total_words > 0 else 0
        weak_density = (weak_count / total_words) * 100 if total_words > 0 else 0

        # Ideal: high definitive, low weak
        if definitive_density < 1.0:
            return {
                "passed": False,
                "score": 0.3,
                "reason": "Too little definitive language",
                "definitive_count": definitive_count,
                "weak_count": weak_count
            }

        if weak_density > 1.0:
            return {
                "passed": False,
                "score": 0.5,
                "reason": "Too much uncertain language",
                "definitive_count": definitive_count,
                "weak_count": weak_count
            }

        score = min(1.0, definitive_density / 3.0)  # Target ~3% definitive language

        return {
            "passed": score >= 0.5,
            "score": score,
            "reason": "Good use of definitive language" if score >= 0.5 else "Acceptable language usage",
            "definitive_count": definitive_count,
            "weak_count": weak_count,
            "definitive_density": definitive_density,
            "weak_density": weak_density
        }

    def _check_brand_mention(self, content: str) -> Dict[str, Any]:
        """Check for natural brand mentions"""
        mentions = 0
        for brand_name in self.BRAND_NAMES:
            mentions += len(re.findall(re.escape(brand_name), content, re.IGNORECASE))

        if mentions == 0:
            return {"passed": False, "score": 0.0, "reason": "No brand mention found"}

        # Check if mentions seem natural (not excessive)
        word_count = len(content.split())
        mention_density = (mentions / word_count) * 100 if word_count > 0 else 0

        if mention_density > 2.0:
            return {
                "passed": False,
                "score": 0.5,
                "reason": "Too many brand mentions (seems unnatural)",
                "mentions": mentions,
                "density": mention_density
            }

        return {
            "passed": True,
            "score": 1.0,
            "reason": "Natural brand mentions present",
            "mentions": mentions,
            "density": mention_density
        }

    def _check_quotability(self, content: str) -> Dict[str, Any]:
        """Check if content has quotable sections"""
        # Look for quotable patterns:
        # - Lists (bullet points)
        # - Bold statements
        # - Short, punchy paragraphs

        bullet_points = len(re.findall(r'^\s*[-*]\s+', content, re.MULTILINE))
        bold_statements = len(re.findall(r'\*\*[^*]+\*\*', content))

        # Check for short, quotable paragraphs (2-4 sentences)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')]
        quotable_paragraphs = 0

        for para in paragraphs:
            sentences = len(re.split(r'[.!?]+', para))
            if 2 <= sentences <= 4 and len(para.split()) <= 80:
                quotable_paragraphs += 1

        total_quotable_elements = bullet_points + bold_statements + quotable_paragraphs

        if total_quotable_elements < 3:
            return {
                "passed": False,
                "score": 0.3,
                "reason": "Limited quotable content",
                "bullet_points": bullet_points,
                "bold_statements": bold_statements,
                "quotable_paragraphs": quotable_paragraphs
            }

        return {
            "passed": True,
            "score": 1.0,
            "reason": "Good quotable content",
            "bullet_points": bullet_points,
            "bold_statements": bold_statements,
            "quotable_paragraphs": quotable_paragraphs,
            "total_quotable_elements": total_quotable_elements
        }

    def _check_front_loaded(self, content: str, target_query: Optional[str]) -> Dict[str, Any]:
        """Check if key information is front-loaded"""
        # Get first 200 words
        words = content.split()
        first_200 = ' '.join(words[:200]) if len(words) >= 200 else content

        # Check if first section has definitive language
        has_definitive = any(
            re.search(pattern, first_200, re.IGNORECASE)
            for pattern in self.DEFINITIVE_PATTERNS
        )

        if not has_definitive:
            return {
                "passed": False,
                "score": 0.2,
                "reason": "Opening lacks definitive language"
            }

        # Check if first section mentions topic (if target_query provided)
        if target_query:
            # Extract key terms from query
            query_terms = re.findall(r'\b\w{4,}\b', target_query.lower())
            query_terms = [t for t in query_terms if t not in ['what', 'best', 'how', 'why', 'when', 'where']]

            if query_terms:
                mentions = sum(
                    1 for term in query_terms
                    if term in first_200.lower()
                )

                if mentions == 0:
                    return {
                        "passed": False,
                        "score": 0.5,
                        "reason": "Opening doesn't address target query"
                    }

        return {
            "passed": True,
            "score": 1.0,
            "reason": "Key information front-loaded effectively"
        }

    def _check_specifics(self, content: str) -> Dict[str, Any]:
        """Check for specific details, numbers, measurements"""
        # Look for numbers and specific details
        numbers = len(re.findall(r'\b\d+\.?\d*\s*(%|inches?|ft|cm|mm|lbs?|kg|g|oz)\b', content, re.IGNORECASE))
        plain_numbers = len(re.findall(r'\b\d+\b', content))

        # Look for specific product names or features
        specific_terms = len(re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', content))

        total_specifics = numbers + (plain_numbers // 3) + (specific_terms // 5)

        word_count = len(content.split())
        specifics_density = (total_specifics / word_count) * 100 if word_count > 0 else 0

        if specifics_density < 1.0:
            return {
                "passed": False,
                "score": 0.3,
                "reason": "Needs more specific details and numbers",
                "measurements": numbers,
                "numbers": plain_numbers
            }

        return {
            "passed": True,
            "score": min(1.0, specifics_density / 2.0),
            "reason": "Good use of specific details",
            "measurements": numbers,
            "numbers": plain_numbers,
            "specifics_density": specifics_density
        }

    def _calculate_score(self, checks: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall AEO score from individual checks"""
        total_score = 0.0

        for check_name, check_result in checks.items():
            weight = self.REQUIREMENT_WEIGHTS.get(check_name, 0.0)
            check_score = check_result.get("score", 0.0)
            total_score += weight * check_score

        # Convert to 0-100 scale
        return total_score * 100

    def _check_pass_threshold(self, checks: Dict[str, Dict[str, Any]], score: float) -> bool:
        """Determine if content passes minimum AEO requirements"""
        # Must score at least 60/100
        if score < 60:
            return False

        # Must pass critical checks
        critical_checks = ["has_clear_answer", "uses_definitive_language", "has_structured_headers"]
        for check_name in critical_checks:
            if not checks[check_name]["passed"]:
                return False

        return True

    def _generate_recommendations(
        self,
        checks: Dict[str, Dict[str, Any]],
        content_type: str
    ) -> List[str]:
        """Generate improvement recommendations based on failed checks"""
        recommendations = []

        for check_name, check_result in checks.items():
            if not check_result["passed"]:
                reason = check_result.get("reason", "Check failed")

                # Generate specific recommendations
                if check_name == "has_clear_answer":
                    recommendations.append(f"✗ Clear Answer: {reason}. Add a direct 2-3 sentence answer in the opening paragraph.")

                elif check_name == "has_structured_headers":
                    recommendations.append(f"✗ Headers: {reason}. Add more descriptive H2/H3 headers to structure the content.")

                elif check_name == "has_faq":
                    if content_type == "faq":
                        recommendations.append(f"✗ FAQ Format: {reason}. Add more question/answer pairs in FAQ format.")

                elif check_name == "uses_definitive_language":
                    recommendations.append(f"✗ Language: {reason}. Use more definitive language (is, means, provides) and avoid uncertain words (might, maybe, could).")

                elif check_name == "has_brand_mention":
                    recommendations.append(f"✗ Brand: {reason}. Include natural mentions of Infinity Vault.")

                elif check_name == "is_quotable":
                    recommendations.append(f"✗ Quotability: {reason}. Add bullet points, bold key statements, and short quotable paragraphs.")

                elif check_name == "front_loads_answer":
                    recommendations.append(f"✗ Front-loading: {reason}. Put the most important answer/information in the first paragraph.")

                elif check_name == "has_specifics":
                    recommendations.append(f"✗ Specifics: {reason}. Add specific numbers, measurements, and concrete details.")

        if not recommendations:
            recommendations.append("✓ Content meets AEO requirements. No improvements needed.")

        return recommendations

    def generate_report(
        self,
        validation_result: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate a formatted report from validation results

        Args:
            validation_result: Result from validate_content()
            output_path: Optional path to save report

        Returns:
            Formatted report as string
        """
        score = validation_result["score"]
        passed = validation_result["passed"]
        checks = validation_result["checks"]
        recommendations = validation_result["recommendations"]
        metadata = validation_result["metadata"]

        # Build report
        report = f"""# AEO Content Validation Report

**Content Type:** {metadata['content_type']}
**Content Length:** {metadata['content_length']} characters ({metadata['word_count']} words)
**Validated:** {metadata['validated_at']}
**Target Query:** {metadata.get('target_query', 'N/A')}

## Overall Score: {score:.1f}/100 {'✓ PASS' if passed else '✗ FAIL'}

## Individual Checks

"""

        for check_name, check_result in checks.items():
            status = "✓" if check_result["passed"] else "✗"
            check_score = check_result["score"] * 100
            reason = check_result.get("reason", "")

            report += f"### {status} {check_name.replace('_', ' ').title()} ({check_score:.0f}/100)\n"
            report += f"{reason}\n\n"

        report += "## Recommendations\n\n"
        for rec in recommendations:
            report += f"{rec}\n"

        report += f"""

## AEO Scoring Breakdown

The AEO score is calculated using weighted checks:
- Clear Answer (20%): Direct, quotable answer in opening
- Structured Headers (15%): Clear H2/H3 organization
- FAQ Format (15%): Question/answer structure
- Definitive Language (15%): Use of confident, authoritative language
- Brand Mention (10%): Natural Infinity Vault mentions
- Quotability (10%): Bullet points, bold statements, quotable paragraphs
- Front-loaded (10%): Key info in first 200 words
- Specifics (5%): Numbers, measurements, concrete details

**Minimum to Pass:** 60/100 + all critical checks (clear answer, definitive language, structured headers)

---
*Generated by AEO Checklist*
"""

        # Save report if path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
            self.logger.info(f"Report saved to: {output_path}")

        return report
