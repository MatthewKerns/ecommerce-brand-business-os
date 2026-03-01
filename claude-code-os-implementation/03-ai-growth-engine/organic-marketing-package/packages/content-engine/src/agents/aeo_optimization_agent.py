"""
AEO (Answer Engine Optimization) Agent - Consolidated

Combines content generation (formerly AEOAgent) and content analysis/scoring
(formerly AEOAnalyzer) into a single unified agent for AEO optimization.

Content Generation:
- FAQ schema and content generation
- Product schema markup
- AI-optimized content creation
- Comparison content for "best" and "vs" queries

Content Analysis:
- Multi-dimensional AEO scoring (structure, definitiveness, quotability, etc.)
- Content optimization recommendations
- Progress tracking over time
- Batch content analysis
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


# Import the original implementations to compose into the consolidated class
from .aeo_agent import AEOAgent as _AEOAgentBase
from .aeo_analyzer import AEOAnalyzer as _AEOAnalyzerBase, AEO_SCORING_WEIGHTS, GRADE_THRESHOLDS


class AEOOptimizationAgent(_AEOAgentBase):
    """
    Unified AEO Optimization Agent combining content generation and analysis.

    Inherits all content generation methods from AEOAgent and delegates
    analysis methods to an internal AEOAnalyzer instance.

    Content Generation (from AEOAgent):
        - generate_faq_schema()
        - generate_faq_content()
        - generate_product_schema()
        - generate_ai_optimized_content()
        - generate_comparison_content()

    Content Analysis (from AEOAnalyzer):
        - analyze_content()
        - analyze_and_save()
        - batch_analyze()
        - track_progress()
        - generate_optimization_report()
    """

    def __init__(self):
        super().__init__()
        # Override agent_name for the consolidated agent
        self.agent_name = "aeo_optimization_agent"
        # Compose the analyzer for analysis methods
        self._analyzer = _AEOAnalyzerBase()
        self.logger.info("AEO Optimization Agent initialized (generation + analysis)")

    # --- Delegated Analysis Methods ---

    def analyze_content(
        self,
        content: str,
        target_queries: Optional[List[str]] = None,
        content_url: Optional[str] = None,
        content_type: str = "article",
    ) -> Dict[str, Any]:
        """Analyze content for AEO citation potential. Delegates to AEOAnalyzer."""
        return self._analyzer.analyze_content(content, target_queries, content_url, content_type)

    def analyze_and_save(
        self,
        content: str,
        output_filename: Optional[str] = None,
        target_queries: Optional[List[str]] = None,
        content_url: Optional[str] = None,
        content_type: str = "article",
    ) -> Dict[str, Any]:
        """Analyze content and save results. Delegates to AEOAnalyzer."""
        return self._analyzer.analyze_and_save(
            content, output_filename, target_queries, content_url, content_type
        )

    def batch_analyze(
        self,
        content_items: List[Dict[str, Any]],
        save_results: bool = True,
    ) -> Dict[str, Any]:
        """Batch analyze multiple content items. Delegates to AEOAnalyzer."""
        return self._analyzer.batch_analyze(content_items, save_results)

    def track_progress(
        self,
        content_url: str,
        current_score: float,
        previous_score: Optional[float] = None,
        content_type: str = "article",
    ) -> Dict[str, Any]:
        """Track AEO score progress over time. Delegates to AEOAnalyzer."""
        return self._analyzer.track_progress(
            content_url, current_score, previous_score, content_type
        )

    def generate_optimization_report(
        self,
        content_items: Optional[List[Dict[str, Any]]] = None,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Generate an AEO optimization report. Delegates to AEOAnalyzer."""
        return self._analyzer.generate_optimization_report(content_items, days)
