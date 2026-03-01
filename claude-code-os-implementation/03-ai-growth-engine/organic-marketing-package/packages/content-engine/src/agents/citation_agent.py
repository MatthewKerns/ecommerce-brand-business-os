"""
Citation Agent - Consolidated

Combines real-time AI assistant monitoring (formerly CitationMonitoringAgent) and
higher-level citation tracking workflows (formerly CitationTracker) into a single
unified agent for brand citation management.

Real-Time Monitoring (from CitationMonitoringAgent):
- Query AI assistants (ChatGPT, Claude, Perplexity)
- Analyze brand mentions and citation positions
- Compare competitor citations
- Generate optimization recommendations
- Detect citation alerts

Citation Tracking (from CitationTracker):
- Citation summaries and trend analysis
- Gap analysis and opportunity identification
- Opportunity scoring
- Improvement recommendations
- Tracking reports and history
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from database.connection import get_db_session
from config.config import BRAND_NAME

# Import the original implementations to compose into the consolidated class
from .citation_monitoring_agent import CitationMonitoringAgent as _CitationMonitoringBase
from .citation_tracker import CitationTracker as _CitationTrackerBase


class CitationAgent(_CitationMonitoringBase):
    """
    Unified Citation Agent combining real-time monitoring and tracking workflows.

    Inherits all real-time monitoring methods from CitationMonitoringAgent and
    delegates tracking/analysis methods to an internal CitationTracker instance.

    Real-Time Monitoring (from CitationMonitoringAgent):
        - query_ai_assistant()
        - analyze_citation()
        - compare_competitors()
        - generate_recommendations()
        - detect_alerts()
        - get_available_platforms()

    Citation Tracking (from CitationTracker):
        - get_citation_summary()
        - identify_citation_gaps()
        - score_citation_opportunity()
        - generate_improvement_recommendations()
        - check_citation_alerts()
        - generate_tracking_report()
        - record_tracking_result()
        - get_tracking_history()
    """

    def __init__(self):
        super().__init__()
        # Override agent_name for the consolidated agent
        self.agent_name = "citation_agent"
        # Compose the tracker for tracking methods
        self._tracker = _CitationTrackerBase()
        self.logger.info("Citation Agent initialized (monitoring + tracking)")

    # --- Delegated Tracking Methods ---

    def get_citation_summary(
        self,
        days: int = 30,
        platform: Optional[str] = None,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Get citation summary for a time period. Delegates to CitationTracker."""
        return self._tracker.get_citation_summary(days, platform, db_session)

    def identify_citation_gaps(
        self,
        query_categories: Optional[List[str]] = None,
        platforms: Optional[List[str]] = None,
        days: int = 30,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Identify gaps in citation coverage. Delegates to CitationTracker."""
        return self._tracker.identify_citation_gaps(
            query_categories, platforms, days, db_session
        )

    def score_citation_opportunity(
        self,
        query: str,
        category: str,
        current_citations: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Score a citation opportunity. Delegates to CitationTracker."""
        return self._tracker.score_citation_opportunity(
            query, category, current_citations
        )

    def generate_improvement_recommendations(
        self,
        days: int = 30,
        max_recommendations: int = 10,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Generate improvement recommendations. Delegates to CitationTracker."""
        return self._tracker.generate_improvement_recommendations(
            days, max_recommendations, db_session
        )

    def check_citation_alerts(
        self,
        days: int = 7,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Check for citation alerts. Delegates to CitationTracker."""
        return self._tracker.check_citation_alerts(days, db_session)

    def generate_tracking_report(
        self,
        days: int = 30,
        include_recommendations: bool = True,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Generate a comprehensive tracking report. Delegates to CitationTracker."""
        return self._tracker.generate_tracking_report(
            days, include_recommendations, db_session
        )

    def record_tracking_result(
        self,
        query: str,
        platform: str,
        brand_mentioned: bool,
        citation_position: Optional[int] = None,
        response_text: Optional[str] = None,
        competitor_mentions: Optional[List[str]] = None,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Record a tracking result. Delegates to CitationTracker."""
        return self._tracker.record_tracking_result(
            query, platform, brand_mentioned, citation_position,
            response_text, competitor_mentions, db_session
        )

    def get_tracking_history(
        self,
        days: int = 30,
        platform: Optional[str] = None,
        query: Optional[str] = None,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Get tracking history. Delegates to CitationTracker."""
        return self._tracker.get_tracking_history(
            days, platform, query, db_session
        )
