"""
SEO Analyzer Utility
Provides on-page SEO analysis and scoring for content optimization
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

from logging_config import get_logger
from exceptions import ValidationError, DataError


@dataclass
class SEOScore:
    """Data class for individual SEO metric scores"""
    metric: str
    score: float  # 0-100 scale
    weight: float  # Importance weight (0-1)
    feedback: str
    issues: List[str]


class SEOAnalyzer:
    """
    Utility for analyzing on-page SEO elements and providing optimization scores

    Analyzes content for keyword optimization, structure, readability,
    and other critical SEO factors.
    """

    # Scoring weights for different SEO factors
    WEIGHTS = {
        'keyword_optimization': 0.30,  # 30% - Most important
        'content_structure': 0.25,     # 25% - Headings and organization
        'content_quality': 0.20,       # 20% - Length and depth
        'readability': 0.15,           # 15% - Ease of reading
        'keyword_placement': 0.10      # 10% - Strategic keyword usage
    }

    # Target ranges for optimal scores
    TARGETS = {
        'keyword_density_min': 0.5,    # 0.5%
        'keyword_density_max': 2.5,    # 2.5%
        'min_word_count': 300,
        'optimal_word_count': 1000,
        'max_word_count': 3000,
        'min_headings': 2,
        'optimal_headings': 5,
        'avg_sentence_length_max': 25
    }

    def __init__(self):
        """Initialize the SEO analyzer"""
        self.logger = get_logger("seo_analyzer")
        self.logger.info("Initialized SEOAnalyzer")

    def analyze_content(
        self,
        content: str,
        target_keyword: Optional[str] = None,
        title: Optional[str] = None,
        meta_description: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Perform comprehensive SEO analysis on content

        Args:
            content: The content to analyze (markdown or plain text)
            target_keyword: Primary keyword to optimize for
            title: Optional page/article title
            meta_description: Optional meta description

        Returns:
            Dictionary containing scores and analysis results

        Raises:
            ValidationError: If content is invalid
        """
        self.logger.info(f"Analyzing content (length: {len(content)} chars)")

        if not content or not content.strip():
            raise ValidationError("content", content, "Content cannot be empty")

        try:
            # Run individual analyses
            keyword_score = self._analyze_keyword_optimization(content, target_keyword)
            structure_score = self._analyze_content_structure(content, title)
            quality_score = self._analyze_content_quality(content)
            readability_score = self._analyze_readability(content)
            placement_score = self._analyze_keyword_placement(content, target_keyword, title)

            # Calculate weighted total score
            total_score = (
                keyword_score.score * self.WEIGHTS['keyword_optimization'] +
                structure_score.score * self.WEIGHTS['content_structure'] +
                quality_score.score * self.WEIGHTS['content_quality'] +
                readability_score.score * self.WEIGHTS['readability'] +
                placement_score.score * self.WEIGHTS['keyword_placement']
            )

            # Collect all issues
            all_issues = []
            all_issues.extend(keyword_score.issues)
            all_issues.extend(structure_score.issues)
            all_issues.extend(quality_score.issues)
            all_issues.extend(readability_score.issues)
            all_issues.extend(placement_score.issues)

            result = {
                'total_score': round(total_score, 2),
                'grade': self._get_grade(total_score),
                'scores': {
                    'keyword_optimization': {
                        'score': round(keyword_score.score, 2),
                        'weight': self.WEIGHTS['keyword_optimization'],
                        'feedback': keyword_score.feedback
                    },
                    'content_structure': {
                        'score': round(structure_score.score, 2),
                        'weight': self.WEIGHTS['content_structure'],
                        'feedback': structure_score.feedback
                    },
                    'content_quality': {
                        'score': round(quality_score.score, 2),
                        'weight': self.WEIGHTS['content_quality'],
                        'feedback': quality_score.feedback
                    },
                    'readability': {
                        'score': round(readability_score.score, 2),
                        'weight': self.WEIGHTS['readability'],
                        'feedback': readability_score.feedback
                    },
                    'keyword_placement': {
                        'score': round(placement_score.score, 2),
                        'weight': self.WEIGHTS['keyword_placement'],
                        'feedback': placement_score.feedback
                    }
                },
                'issues': all_issues,
                'target_keyword': target_keyword,
                'word_count': self._count_words(content),
                'recommendations': self._generate_recommendations(all_issues, total_score)
            }

            self.logger.info(f"Analysis complete. Total score: {total_score:.2f} ({result['grade']})")
            return result

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"SEO analysis failed: {e}", exc_info=True)
            raise DataError("seo_analysis", str(e))

    def _analyze_keyword_optimization(
        self,
        content: str,
        target_keyword: Optional[str]
    ) -> SEOScore:
        """Analyze keyword usage and density"""

        if not target_keyword:
            return SEOScore(
                metric="keyword_optimization",
                score=50.0,  # Neutral score when no keyword provided
                weight=self.WEIGHTS['keyword_optimization'],
                feedback="No target keyword specified",
                issues=["Consider specifying a target keyword for optimization"]
            )

        issues = []
        word_count = self._count_words(content)

        # Count keyword occurrences (case-insensitive)
        keyword_count = len(re.findall(
            r'\b' + re.escape(target_keyword) + r'\b',
            content,
            re.IGNORECASE
        ))

        # Calculate keyword density
        if word_count > 0:
            keyword_density = (keyword_count / word_count) * 100
        else:
            keyword_density = 0

        # Score based on keyword density
        score = 0.0
        if keyword_density < self.TARGETS['keyword_density_min']:
            score = (keyword_density / self.TARGETS['keyword_density_min']) * 50
            issues.append(
                f"Keyword density too low ({keyword_density:.2f}%). "
                f"Target: {self.TARGETS['keyword_density_min']}-{self.TARGETS['keyword_density_max']}%"
            )
        elif keyword_density > self.TARGETS['keyword_density_max']:
            score = max(0, 100 - ((keyword_density - self.TARGETS['keyword_density_max']) * 20))
            issues.append(
                f"Keyword density too high ({keyword_density:.2f}%). "
                f"Risk of keyword stuffing. Target: {self.TARGETS['keyword_density_min']}-{self.TARGETS['keyword_density_max']}%"
            )
        else:
            # Optimal range - score based on proximity to ideal (1.5%)
            ideal_density = 1.5
            deviation = abs(keyword_density - ideal_density)
            score = 100 - (deviation * 20)

        feedback = f"Keyword '{target_keyword}' appears {keyword_count} times ({keyword_density:.2f}% density)"

        return SEOScore(
            metric="keyword_optimization",
            score=max(0, min(100, score)),
            weight=self.WEIGHTS['keyword_optimization'],
            feedback=feedback,
            issues=issues
        )

    def _analyze_content_structure(
        self,
        content: str,
        title: Optional[str]
    ) -> SEOScore:
        """Analyze content structure (headings, hierarchy)"""

        issues = []
        score = 100.0

        # Find all markdown headings
        headings = re.findall(r'^#{1,6}\s+.+$', content, re.MULTILINE)
        heading_count = len(headings)

        # Check for H1 (# heading)
        h1_headings = [h for h in headings if h.startswith('# ') and not h.startswith('## ')]

        if not h1_headings and not title:
            issues.append("Missing H1 heading or title")
            score -= 30
        elif len(h1_headings) > 1:
            issues.append(f"Multiple H1 headings found ({len(h1_headings)}). Should have exactly one.")
            score -= 20

        # Check heading quantity
        if heading_count < self.TARGETS['min_headings']:
            issues.append(
                f"Too few headings ({heading_count}). "
                f"Recommended: at least {self.TARGETS['min_headings']}"
            )
            score -= 25
        elif heading_count >= self.TARGETS['optimal_headings']:
            # Optimal - bonus points for good structure
            score = min(100, score + 10)

        # Check for heading hierarchy
        heading_levels = []
        for heading in headings:
            level = len(re.match(r'^#+', heading).group())
            heading_levels.append(level)

        # Check if headings skip levels (e.g., H1 to H3)
        if heading_levels:
            for i in range(len(heading_levels) - 1):
                if heading_levels[i+1] - heading_levels[i] > 1:
                    issues.append("Heading hierarchy skips levels (e.g., H1 to H3)")
                    score -= 10
                    break

        feedback = f"Found {heading_count} headings with proper structure"
        if issues:
            feedback = f"Found {heading_count} headings. Structure needs improvement."

        return SEOScore(
            metric="content_structure",
            score=max(0, min(100, score)),
            weight=self.WEIGHTS['content_structure'],
            feedback=feedback,
            issues=issues
        )

    def _analyze_content_quality(self, content: str) -> SEOScore:
        """Analyze content quality based on length and depth"""

        issues = []
        word_count = self._count_words(content)

        # Score based on word count
        if word_count < self.TARGETS['min_word_count']:
            score = (word_count / self.TARGETS['min_word_count']) * 60
            issues.append(
                f"Content too short ({word_count} words). "
                f"Minimum: {self.TARGETS['min_word_count']}, Optimal: {self.TARGETS['optimal_word_count']}"
            )
        elif word_count > self.TARGETS['max_word_count']:
            score = max(70, 100 - ((word_count - self.TARGETS['max_word_count']) / 1000 * 5))
            issues.append(
                f"Content very long ({word_count} words). "
                f"Consider breaking into multiple pages. Max recommended: {self.TARGETS['max_word_count']}"
            )
        elif word_count >= self.TARGETS['optimal_word_count']:
            # Optimal length
            score = 100
        else:
            # Between min and optimal
            score = 60 + ((word_count - self.TARGETS['min_word_count']) /
                         (self.TARGETS['optimal_word_count'] - self.TARGETS['min_word_count']) * 40)

        feedback = f"Content length: {word_count} words"

        return SEOScore(
            metric="content_quality",
            score=max(0, min(100, score)),
            weight=self.WEIGHTS['content_quality'],
            feedback=feedback,
            issues=issues
        )

    def _analyze_readability(self, content: str) -> SEOScore:
        """Analyze content readability"""

        issues = []
        score = 100.0

        # Remove markdown formatting for readability analysis
        clean_content = re.sub(r'#{1,6}\s+', '', content)  # Remove heading markers
        clean_content = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', clean_content)  # Remove bold/italic
        clean_content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_content)  # Remove links

        # Split into sentences
        sentences = re.split(r'[.!?]+', clean_content)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return SEOScore(
                metric="readability",
                score=0,
                weight=self.WEIGHTS['readability'],
                feedback="No readable sentences found",
                issues=["Content appears to be empty or improperly formatted"]
            )

        # Calculate average sentence length
        total_words = sum(len(s.split()) for s in sentences)
        avg_sentence_length = total_words / len(sentences) if sentences else 0

        # Score based on sentence length
        if avg_sentence_length > self.TARGETS['avg_sentence_length_max']:
            score -= min(30, (avg_sentence_length - self.TARGETS['avg_sentence_length_max']) * 2)
            issues.append(
                f"Average sentence length too long ({avg_sentence_length:.1f} words). "
                f"Recommended: under {self.TARGETS['avg_sentence_length_max']} words for better readability"
            )

        # Check for paragraph breaks (double newlines)
        paragraphs = content.split('\n\n')
        avg_paragraph_length = len(content.split()) / len(paragraphs) if paragraphs else 0

        if avg_paragraph_length > 150:
            score -= 15
            issues.append("Paragraphs too long. Break into smaller chunks for better readability")

        feedback = f"Average sentence length: {avg_sentence_length:.1f} words"

        return SEOScore(
            metric="readability",
            score=max(0, min(100, score)),
            weight=self.WEIGHTS['readability'],
            feedback=feedback,
            issues=issues
        )

    def _analyze_keyword_placement(
        self,
        content: str,
        target_keyword: Optional[str],
        title: Optional[str]
    ) -> SEOScore:
        """Analyze keyword placement in strategic locations"""

        if not target_keyword:
            return SEOScore(
                metric="keyword_placement",
                score=50.0,
                weight=self.WEIGHTS['keyword_placement'],
                feedback="No target keyword to analyze placement",
                issues=[]
            )

        issues = []
        score = 100.0
        keyword_lower = target_keyword.lower()

        # Check in title/H1
        h1_headings = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
        title_has_keyword = False

        if title and keyword_lower in title.lower():
            title_has_keyword = True
        elif h1_headings and keyword_lower in h1_headings[0].lower():
            title_has_keyword = True

        if not title_has_keyword:
            issues.append("Target keyword not found in title/H1 heading")
            score -= 35

        # Check in first paragraph (first 150 words)
        words = content.split()
        first_para = ' '.join(words[:150])
        if keyword_lower not in first_para.lower():
            issues.append("Target keyword not found in opening paragraph")
            score -= 25

        # Check in subheadings
        all_headings = re.findall(r'^#{2,6}\s+(.+)$', content, re.MULTILINE)
        heading_with_keyword = any(keyword_lower in h.lower() for h in all_headings)

        if all_headings and not heading_with_keyword:
            issues.append("Target keyword not found in any subheadings")
            score -= 20

        # Check in last paragraph (closing)
        last_para = ' '.join(words[-150:]) if len(words) > 150 else ' '.join(words)
        if keyword_lower not in last_para.lower():
            issues.append("Target keyword not found in closing section")
            score -= 20

        feedback = "Keyword placement analysis complete"
        if score == 100:
            feedback = "Excellent keyword placement in all strategic locations"

        return SEOScore(
            metric="keyword_placement",
            score=max(0, min(100, score)),
            weight=self.WEIGHTS['keyword_placement'],
            feedback=feedback,
            issues=issues
        )

    def _count_words(self, content: str) -> int:
        """Count words in content, excluding markdown syntax"""
        # Remove code blocks
        content = re.sub(r'```[\s\S]*?```', '', content)
        # Remove inline code
        content = re.sub(r'`[^`]+`', '', content)
        # Remove markdown links but keep link text
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        # Remove images
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', content)
        # Remove heading markers
        content = re.sub(r'#{1,6}\s+', '', content)
        # Remove bold/italic markers
        content = re.sub(r'[*_]+', '', content)

        # Count words
        words = content.split()
        return len(words)

    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _generate_recommendations(self, issues: List[str], total_score: float) -> List[str]:
        """Generate actionable recommendations based on issues"""
        recommendations = []

        if total_score >= 90:
            recommendations.append("Excellent SEO! Content is well-optimized.")
            return recommendations

        if total_score >= 70:
            recommendations.append("Good SEO foundation. Address minor issues for improvement.")
        elif total_score >= 50:
            recommendations.append("Moderate SEO. Several areas need attention.")
        else:
            recommendations.append("Poor SEO. Major optimization needed.")

        # Add specific recommendations based on common issues
        if any('keyword' in issue.lower() and 'density' in issue.lower() for issue in issues):
            recommendations.append("Adjust keyword usage to achieve 1-2% density for optimal results")

        if any('heading' in issue.lower() for issue in issues):
            recommendations.append("Improve content structure with proper heading hierarchy (H1, H2, H3)")

        if any('short' in issue.lower() or 'word' in issue.lower() for issue in issues):
            recommendations.append("Expand content to at least 1000 words for better ranking potential")

        if any('placement' in issue.lower() for issue in issues):
            recommendations.append("Place target keyword in title, opening, subheadings, and closing")

        if any('sentence' in issue.lower() or 'paragraph' in issue.lower() for issue in issues):
            recommendations.append("Improve readability with shorter sentences and paragraphs")

        return recommendations

    def get_keyword_density(self, content: str, keyword: str) -> float:
        """
        Calculate keyword density for a specific keyword

        Args:
            content: Content to analyze
            keyword: Keyword to calculate density for

        Returns:
            Keyword density as percentage (0-100)
        """
        word_count = self._count_words(content)
        if word_count == 0:
            return 0.0

        keyword_count = len(re.findall(
            r'\b' + re.escape(keyword) + r'\b',
            content,
            re.IGNORECASE
        ))

        return (keyword_count / word_count) * 100

    def validate_seo_basics(self, content: str, target_keyword: str) -> Dict[str, bool]:
        """
        Quick validation of basic SEO requirements

        Args:
            content: Content to validate
            target_keyword: Target keyword

        Returns:
            Dictionary of boolean checks for basic SEO requirements
        """
        checks = {
            'has_h1': bool(re.search(r'^#\s+.+$', content, re.MULTILINE)),
            'has_headings': len(re.findall(r'^#{1,6}\s+.+$', content, re.MULTILINE)) >= self.TARGETS['min_headings'],
            'min_word_count': self._count_words(content) >= self.TARGETS['min_word_count'],
            'keyword_in_content': target_keyword.lower() in content.lower(),
            'keyword_in_h1': False
        }

        # Check if keyword is in H1
        h1_headings = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_headings and target_keyword.lower() in h1_headings[0].lower():
            checks['keyword_in_h1'] = True

        return checks
