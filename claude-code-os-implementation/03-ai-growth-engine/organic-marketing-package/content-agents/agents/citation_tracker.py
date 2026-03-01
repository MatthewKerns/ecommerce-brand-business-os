"""
Citation Tracker Agent

Tracks and monitors brand citations across AI assistant platforms (ChatGPT, Claude,
Perplexity, Google AI). Identifies citation opportunities, gaps, and competitive
landscape. Generates actionable recommendations for improving AI visibility.

This agent works alongside the CitationMonitoringAgent (which handles real-time
querying and analysis) by providing higher-level tracking workflows, scheduled
monitoring runs, gap analysis, and opportunity scoring.
"""
import json
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from database.models import (
    CitationRecord,
    CitationTracking,
    CompetitorCitation,
    OptimizationRecommendation,
    AlertRecord,
)
from database.connection import get_db_session
from config.config import (
    BRAND_NAME,
    COMPETITOR_BRANDS,
    CITATION_MONITORING_TARGETS,
    AEO_PERPLEXITY_QUERIES,
    AEO_OPENAI_QUERIES,
    AEO_GEMINI_QUERIES,
    HIGH_VALUE_SEARCH_TERMS,
    AEO_OUTPUT_DIR,
    AEO_CONFIG,
    AEO_PLATFORM_CONFIG,
)
from exceptions import ContentGenerationError


# Opportunity score weights
OPPORTUNITY_WEIGHTS = {
    'query_volume': 0.30,       # How popular/important the query is
    'current_gap': 0.25,        # Brand not cited but competitors are
    'competitor_density': 0.20, # How many competitors are cited
    'improvement_ease': 0.15,   # How easy it is to improve citation
    'business_impact': 0.10,    # Revenue potential of the query category
}

# Query categories and their business impact scores (0-100)
QUERY_CATEGORY_IMPACT = {
    'product_discovery': 90,
    'purchase_intent': 95,
    'comparison': 85,
    'problem_solving': 70,
    'educational': 50,
    'other': 40,
}


class CitationTracker(BaseAgent):
    """Agent specialized in tracking and analyzing brand citations across AI platforms"""

    def __init__(self):
        """
        Initialize the Citation Tracker Agent

        Raises:
            AgentInitializationError: If agent initialization fails
        """
        super().__init__(agent_name="citation_tracker")
        self.brand_name = BRAND_NAME
        self.competitor_brands = COMPETITOR_BRANDS
        self.monitoring_targets = CITATION_MONITORING_TARGETS
        self.logger.info(
            f"Citation Tracker initialized: brand='{self.brand_name}', "
            f"competitors={len(self.competitor_brands)}, "
            f"monitoring_targets={len(self.monitoring_targets)}"
        )

    def get_citation_summary(
        self,
        days: int = 30,
        platform: Optional[str] = None,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Get a comprehensive summary of citation performance over a time period

        Args:
            days: Number of days to analyze (default: 30)
            platform: Optional filter by AI platform (chatgpt, claude, perplexity, gemini)
            db_session: Optional database session

        Returns:
            Dictionary containing:
                - overview: High-level metrics (total queries, citation rate, trend)
                - by_platform: Per-platform breakdown
                - by_category: Per-query-category breakdown
                - top_cited_queries: Queries where brand is most often cited
                - uncited_queries: Queries where brand is never cited
                - competitor_comparison: How competitors compare
                - alerts: Any active alerts

        Raises:
            ValueError: If days is invalid
            ContentGenerationError: For unexpected errors
        """
        if days <= 0:
            raise ValueError("days parameter must be greater than 0")

        self.logger.info(f"Generating citation summary: days={days}, platform={platform or 'all'}")

        session_provided = db_session is not None
        if not session_provided:
            db_session = get_db_session()

        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Base query for brand citations
            query = db_session.query(CitationRecord).filter(
                CitationRecord.test_date >= start_date,
            )
            if platform:
                query = query.filter(CitationRecord.ai_assistant == platform.lower())

            records = query.all()
            total_queries = len(records)
            cited_count = sum(1 for r in records if r.brand_mentioned)
            citation_rate = (cited_count / total_queries * 100) if total_queries > 0 else 0

            # Recommended count (stronger signal than just mentioned)
            recommended_count = sum(1 for r in records if r.brand_recommended)

            # Per-platform breakdown
            by_platform = {}
            for plat in ['chatgpt', 'claude', 'perplexity', 'gemini', 'copilot']:
                plat_records = [r for r in records if r.ai_assistant == plat]
                if plat_records:
                    plat_cited = sum(1 for r in plat_records if r.brand_mentioned)
                    by_platform[plat] = {
                        'total_queries': len(plat_records),
                        'cited': plat_cited,
                        'citation_rate': round(plat_cited / len(plat_records) * 100, 1),
                    }

            # Per-category breakdown
            by_category = {}
            for cat in ['product_discovery', 'problem_solving', 'comparison',
                        'purchase_intent', 'educational', 'other']:
                cat_records = [r for r in records if r.query_category == cat]
                if cat_records:
                    cat_cited = sum(1 for r in cat_records if r.brand_mentioned)
                    by_category[cat] = {
                        'total_queries': len(cat_records),
                        'cited': cat_cited,
                        'citation_rate': round(cat_cited / len(cat_records) * 100, 1),
                    }

            # Top cited queries (queries where brand is most cited)
            cited_records = [r for r in records if r.brand_mentioned]
            query_citation_map = {}
            for r in cited_records:
                q = r.query
                if q not in query_citation_map:
                    query_citation_map[q] = {'count': 0, 'platforms': set()}
                query_citation_map[q]['count'] += 1
                query_citation_map[q]['platforms'].add(r.ai_assistant)

            top_cited = sorted(
                [
                    {
                        'query': q,
                        'citation_count': data['count'],
                        'platforms': list(data['platforms']),
                    }
                    for q, data in query_citation_map.items()
                ],
                key=lambda x: x['citation_count'],
                reverse=True,
            )[:10]

            # Uncited queries (queries where brand is never mentioned)
            uncited_records = [r for r in records if not r.brand_mentioned]
            uncited_queries_set = set()
            for r in uncited_records:
                # Only include if brand was NEVER cited for this query
                q = r.query
                if q not in query_citation_map:
                    uncited_queries_set.add(q)
            uncited_queries = list(uncited_queries_set)[:10]

            # Competitor comparison
            comp_query = db_session.query(CompetitorCitation).filter(
                CompetitorCitation.query_timestamp >= start_date,
            )
            if platform:
                comp_query = comp_query.filter(
                    CompetitorCitation.ai_platform == platform.lower()
                )
            comp_records = comp_query.all()

            competitor_stats = {}
            for comp_name in self.competitor_brands:
                comp_recs = [r for r in comp_records if r.competitor_name == comp_name]
                if comp_recs:
                    comp_cited = sum(1 for r in comp_recs if r.competitor_mentioned)
                    competitor_stats[comp_name] = {
                        'total_queries': len(comp_recs),
                        'cited': comp_cited,
                        'citation_rate': round(comp_cited / len(comp_recs) * 100, 1),
                    }

            # Active alerts
            active_alerts = db_session.query(AlertRecord).filter(
                AlertRecord.status == 'active',
            ).order_by(AlertRecord.triggered_at.desc()).limit(5).all()

            alerts = [
                {
                    'id': alert.id,
                    'type': alert.alert_type,
                    'severity': alert.alert_severity,
                    'title': alert.title,
                    'triggered_at': alert.triggered_at.isoformat() if alert.triggered_at else None,
                }
                for alert in active_alerts
            ]

            # Calculate trend vs previous period
            prev_start = start_date - timedelta(days=days)
            prev_query = db_session.query(CitationRecord).filter(
                CitationRecord.test_date >= prev_start,
                CitationRecord.test_date < start_date,
            )
            if platform:
                prev_query = prev_query.filter(
                    CitationRecord.ai_assistant == platform.lower()
                )
            prev_records = prev_query.all()
            prev_total = len(prev_records)
            prev_cited = sum(1 for r in prev_records if r.brand_mentioned)
            prev_rate = (prev_cited / prev_total * 100) if prev_total > 0 else 0
            trend_change = citation_rate - prev_rate

            result = {
                'overview': {
                    'time_period_days': days,
                    'total_queries': total_queries,
                    'cited_count': cited_count,
                    'recommended_count': recommended_count,
                    'citation_rate': round(citation_rate, 1),
                    'trend_change': round(trend_change, 1),
                    'trend_direction': 'improving' if trend_change > 0 else (
                        'declining' if trend_change < 0 else 'stable'
                    ),
                },
                'by_platform': by_platform,
                'by_category': by_category,
                'top_cited_queries': top_cited,
                'uncited_queries': uncited_queries,
                'competitor_comparison': competitor_stats,
                'alerts': alerts,
            }

            self.logger.info(
                f"Citation summary: rate={citation_rate:.1f}%, "
                f"trend={trend_change:+.1f}%, queries={total_queries}"
            )

            return result

        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Error generating citation summary: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(self.agent_name, "", error_msg)
        finally:
            if not session_provided and db_session:
                db_session.close()

    def identify_citation_gaps(
        self,
        days: int = 30,
        db_session: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        """
        Identify queries where competitors are cited but the brand is not

        These represent the highest-priority opportunities for content improvement.

        Args:
            days: Number of days to analyze
            db_session: Optional database session

        Returns:
            List of gap dictionaries sorted by opportunity score, each containing:
                - query: The query text
                - category: Query category
                - competitors_cited: List of competitors cited for this query
                - platforms_affected: Which platforms don't cite the brand
                - opportunity_score: Calculated opportunity score (0-100)
                - recommended_actions: Specific actions to close the gap
        """
        self.logger.info(f"Identifying citation gaps over {days} days")

        session_provided = db_session is not None
        if not session_provided:
            db_session = get_db_session()

        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            # Get all brand citation records
            brand_records = db_session.query(CitationRecord).filter(
                CitationRecord.test_date >= start_date,
            ).all()

            # Get all competitor citation records
            comp_records = db_session.query(CompetitorCitation).filter(
                CompetitorCitation.query_timestamp >= start_date,
            ).all()

            # Build query-level maps
            # Brand: which queries are NOT cited
            uncited_queries = {}
            for r in brand_records:
                q = r.query
                if q not in uncited_queries:
                    uncited_queries[q] = {
                        'cited': False,
                        'category': r.query_category,
                        'platforms': set(),
                    }
                if r.brand_mentioned:
                    uncited_queries[q]['cited'] = True
                uncited_queries[q]['platforms'].add(r.ai_assistant)

            # Filter to only uncited queries
            gap_queries = {
                q: data for q, data in uncited_queries.items()
                if not data['cited']
            }

            # Competitor: which queries have competitor citations
            competitor_by_query = {}
            for r in comp_records:
                q = r.query
                if q not in competitor_by_query:
                    competitor_by_query[q] = {
                        'competitors': set(),
                        'platforms': set(),
                    }
                if r.competitor_mentioned:
                    competitor_by_query[q]['competitors'].add(r.competitor_name)
                    competitor_by_query[q]['platforms'].add(r.ai_platform)

            # Find gaps: uncited brand queries where competitors ARE cited
            gaps = []
            for query_text, gap_data in gap_queries.items():
                comp_data = competitor_by_query.get(query_text, {})
                competitors_cited = list(comp_data.get('competitors', set()))

                # Calculate opportunity score
                category = gap_data.get('category', 'other')
                business_impact = QUERY_CATEGORY_IMPACT.get(category, 40)
                competitor_density = min(len(competitors_cited) * 25, 100)
                current_gap = 100 if competitors_cited else 30
                platforms_count = len(gap_data['platforms'])
                improvement_ease = max(100 - competitor_density, 20)

                opportunity_score = (
                    OPPORTUNITY_WEIGHTS['business_impact'] * business_impact
                    + OPPORTUNITY_WEIGHTS['current_gap'] * current_gap
                    + OPPORTUNITY_WEIGHTS['competitor_density'] * competitor_density
                    + OPPORTUNITY_WEIGHTS['improvement_ease'] * improvement_ease
                    + OPPORTUNITY_WEIGHTS['query_volume'] * min(platforms_count * 30, 100)
                )

                # Generate recommended actions
                actions = self._generate_gap_actions(
                    query_text, category, competitors_cited, list(gap_data['platforms'])
                )

                gaps.append({
                    'query': query_text,
                    'category': category,
                    'competitors_cited': competitors_cited,
                    'platforms_affected': list(gap_data['platforms']),
                    'opportunity_score': round(opportunity_score, 1),
                    'recommended_actions': actions,
                })

            # Sort by opportunity score descending
            gaps.sort(key=lambda x: x['opportunity_score'], reverse=True)

            self.logger.info(f"Identified {len(gaps)} citation gaps")
            return gaps

        except Exception as e:
            error_msg = f"Error identifying citation gaps: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(self.agent_name, "", error_msg)
        finally:
            if not session_provided and db_session:
                db_session.close()

    def _generate_gap_actions(
        self,
        query: str,
        category: str,
        competitors_cited: List[str],
        platforms: List[str],
    ) -> List[str]:
        """
        Generate specific recommended actions to close a citation gap

        Args:
            query: The query text
            category: Query category
            competitors_cited: Competitors that are cited for this query
            platforms: Platforms where the gap exists

        Returns:
            List of actionable recommendation strings
        """
        actions = []

        if category in ('product_discovery', 'purchase_intent'):
            actions.append(
                f"Create targeted landing page or blog post that directly answers: '{query}'"
            )
            actions.append(
                "Include definitive product recommendations with specific features and comparisons"
            )

        if category == 'comparison':
            comp_list = ", ".join(competitors_cited[:3]) if competitors_cited else "competitors"
            actions.append(
                f"Create comparison content: {BRAND_NAME} vs {comp_list}"
            )
            actions.append(
                "Use structured comparison tables with specific measurements and features"
            )

        if category in ('problem_solving', 'educational'):
            actions.append(
                f"Create comprehensive guide content addressing: '{query}'"
            )
            actions.append(
                f"Position {BRAND_NAME} as the expert solution within the guide"
            )

        if competitors_cited:
            actions.append(
                f"Analyze content from {competitors_cited[0]} to understand why they are cited"
            )

        if len(platforms) >= 2:
            actions.append(
                "Optimize content structure for multi-platform citation (headers, lists, direct answers)"
            )

        return actions

    def score_citation_opportunity(
        self,
        query: str,
        category: str = "other",
        competitor_count: int = 0,
        current_citation_rate: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Score a specific query's citation opportunity potential

        Args:
            query: The query text
            category: Query category
            competitor_count: Number of competitors already cited
            current_citation_rate: Current brand citation rate for this query (0-100)

        Returns:
            Dictionary with opportunity score and breakdown
        """
        business_impact = QUERY_CATEGORY_IMPACT.get(category, 40)
        current_gap = 100 - current_citation_rate
        competitor_density = min(competitor_count * 25, 100)
        improvement_ease = max(100 - competitor_density, 20)

        # Estimate query volume based on match with high-value terms
        query_lower = query.lower()
        volume_score = 0
        for term in HIGH_VALUE_SEARCH_TERMS:
            term_words = term.lower().split()
            matches = sum(1 for w in term_words if w in query_lower)
            if matches >= len(term_words) * 0.5:
                volume_score = max(volume_score, 80)
                break
        if volume_score == 0:
            volume_score = 40  # Default for unknown queries

        opportunity_score = (
            OPPORTUNITY_WEIGHTS['query_volume'] * volume_score
            + OPPORTUNITY_WEIGHTS['current_gap'] * current_gap
            + OPPORTUNITY_WEIGHTS['competitor_density'] * competitor_density
            + OPPORTUNITY_WEIGHTS['improvement_ease'] * improvement_ease
            + OPPORTUNITY_WEIGHTS['business_impact'] * business_impact
        )

        return {
            'query': query,
            'opportunity_score': round(opportunity_score, 1),
            'breakdown': {
                'query_volume': round(volume_score, 1),
                'current_gap': round(current_gap, 1),
                'competitor_density': round(competitor_density, 1),
                'improvement_ease': round(improvement_ease, 1),
                'business_impact': round(business_impact, 1),
            },
            'priority': (
                'high' if opportunity_score >= 70
                else 'medium' if opportunity_score >= 45
                else 'low'
            ),
        }

    def generate_improvement_recommendations(
        self,
        days: int = 30,
        max_recommendations: int = 10,
        save_to_db: bool = True,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Generate prioritized recommendations for improving brand citation rates

        Analyzes citation data, gaps, and competitor landscape to produce actionable
        recommendations with expected impact scores.

        Args:
            days: Number of days of data to analyze
            max_recommendations: Maximum number of recommendations to generate
            save_to_db: Whether to save recommendations to database
            db_session: Optional database session

        Returns:
            Dictionary with recommendations list and summary
        """
        self.logger.info(
            f"Generating improvement recommendations: days={days}, max={max_recommendations}"
        )

        session_provided = db_session is not None
        if not session_provided:
            db_session = get_db_session()

        try:
            # Get citation summary for context
            summary = self.get_citation_summary(days=days, db_session=db_session)

            # Get citation gaps
            gaps = self.identify_citation_gaps(days=days, db_session=db_session)

            recommendations = []

            # 1. Gap-based recommendations (highest priority)
            for gap in gaps[:5]:
                if gap['opportunity_score'] >= 50:
                    rec = {
                        'type': 'content',
                        'title': f"Close citation gap: {gap['query'][:80]}",
                        'description': (
                            f"Brand is not cited for the query '{gap['query']}' while "
                            f"{len(gap['competitors_cited'])} competitor(s) are cited "
                            f"({', '.join(gap['competitors_cited'][:3])}). "
                            f"Create targeted content to address this query directly."
                        ),
                        'priority': 'high' if gap['opportunity_score'] >= 70 else 'medium',
                        'expected_impact': int(gap['opportunity_score']),
                        'implementation_effort': 'medium',
                        'ai_platform': 'all',
                        'actions': gap['recommended_actions'],
                    }
                    recommendations.append(rec)

            # 2. Platform-specific recommendations
            overview = summary.get('overview', {})
            for plat, plat_data in summary.get('by_platform', {}).items():
                if plat_data['citation_rate'] < 25 and plat_data['total_queries'] >= 3:
                    recommendations.append({
                        'type': 'technical',
                        'title': f"Improve citation rate on {plat.title()}",
                        'description': (
                            f"Brand citation rate on {plat.title()} is only "
                            f"{plat_data['citation_rate']}% across {plat_data['total_queries']} "
                            f"queries. Research {plat.title()}'s content preferences and optimize "
                            f"content structure accordingly."
                        ),
                        'priority': 'medium',
                        'expected_impact': 55,
                        'implementation_effort': 'medium',
                        'ai_platform': plat,
                        'actions': [
                            f"Analyze what content structure {plat.title()} prefers to cite",
                            "Ensure content includes structured data and clear headers",
                            f"Test different content formats for {plat.title()} citation improvement",
                        ],
                    })

            # 3. Category-specific recommendations
            for cat, cat_data in summary.get('by_category', {}).items():
                impact = QUERY_CATEGORY_IMPACT.get(cat, 40)
                if cat_data['citation_rate'] < 30 and impact >= 70:
                    recommendations.append({
                        'type': 'content',
                        'title': f"Improve {cat.replace('_', ' ')} citations",
                        'description': (
                            f"Citation rate for '{cat.replace('_', ' ')}' queries is "
                            f"{cat_data['citation_rate']}%. This is a high-impact category "
                            f"(business impact: {impact}/100). Focus content creation on "
                            f"answering these types of queries authoritatively."
                        ),
                        'priority': 'high',
                        'expected_impact': impact,
                        'implementation_effort': 'high',
                        'ai_platform': 'all',
                        'actions': [
                            f"Create 3-5 cornerstone articles for {cat.replace('_', ' ')} queries",
                            "Use definitive language and specific product recommendations",
                            "Include FAQ schema and structured data",
                        ],
                    })

            # 4. Trend-based recommendation
            trend_change = overview.get('trend_change', 0)
            if trend_change < -5:
                recommendations.append({
                    'type': 'content',
                    'title': 'Citation rate declining - urgent content refresh needed',
                    'description': (
                        f"Citation rate has dropped {abs(trend_change):.1f} percentage points "
                        f"compared to previous period. Review and update existing content for "
                        f"freshness signals, accuracy, and authoritative language."
                    ),
                    'priority': 'high',
                    'expected_impact': 65,
                    'implementation_effort': 'medium',
                    'ai_platform': 'all',
                    'actions': [
                        "Audit top-performing content for outdated information",
                        "Add current year references and updated statistics",
                        "Refresh headlines and opening paragraphs with stronger direct answers",
                    ],
                })

            # Sort by expected impact and limit
            recommendations.sort(key=lambda x: x['expected_impact'], reverse=True)
            recommendations = recommendations[:max_recommendations]

            # Save to database if requested
            if save_to_db:
                self._save_recommendations(recommendations, db_session)

            # Build summary
            rec_summary = {
                'total_recommendations': len(recommendations),
                'high_priority': sum(1 for r in recommendations if r['priority'] == 'high'),
                'medium_priority': sum(1 for r in recommendations if r['priority'] == 'medium'),
                'low_priority': sum(1 for r in recommendations if r['priority'] == 'low'),
                'by_type': {},
            }
            for rec in recommendations:
                rec_type = rec['type']
                rec_summary['by_type'][rec_type] = rec_summary['by_type'].get(rec_type, 0) + 1

            result = {
                'recommendations': recommendations,
                'summary': rec_summary,
                'context': {
                    'citation_rate': overview.get('citation_rate', 0),
                    'trend': overview.get('trend_direction', 'unknown'),
                    'total_gaps': len(gaps),
                    'analysis_period_days': days,
                },
            }

            self.logger.info(
                f"Generated {len(recommendations)} recommendations: "
                f"high={rec_summary['high_priority']}, medium={rec_summary['medium_priority']}"
            )

            return result

        except Exception as e:
            error_msg = f"Error generating recommendations: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(self.agent_name, "", error_msg)
        finally:
            if not session_provided and db_session:
                db_session.close()

    def _save_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        db_session: Session,
    ) -> None:
        """
        Save recommendations to the database

        Args:
            recommendations: List of recommendation dictionaries
            db_session: Database session
        """
        self.logger.info(f"Saving {len(recommendations)} recommendations to database")

        for rec in recommendations:
            db_rec = OptimizationRecommendation(
                recommendation_type=rec['type'],
                title=rec['title'][:255],
                description=rec['description'],
                priority=rec['priority'],
                status='pending',
                ai_platform=rec.get('ai_platform', 'all'),
                expected_impact=rec.get('expected_impact'),
                implementation_effort=rec.get('implementation_effort'),
                recommendation_metadata=json.dumps({
                    'source': 'citation_tracker',
                    'actions': rec.get('actions', []),
                    'generated_at': datetime.utcnow().isoformat(),
                }),
            )
            db_session.add(db_rec)

        db_session.commit()
        self.logger.info("Recommendations saved successfully")

    def check_citation_alerts(
        self,
        db_session: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        """
        Check for citation alert conditions and create alerts as needed

        Monitors for: citation rate drops, competitor gains, threshold breaches.

        Args:
            db_session: Optional database session

        Returns:
            List of newly created alert dictionaries
        """
        self.logger.info("Checking citation alert conditions")

        session_provided = db_session is not None
        if not session_provided:
            db_session = get_db_session()

        try:
            new_alerts = []

            # Get current and previous period data
            current_summary = self.get_citation_summary(days=7, db_session=db_session)
            prev_summary = self.get_citation_summary(days=14, db_session=db_session)

            current_rate = current_summary['overview']['citation_rate']
            prev_rate = prev_summary['overview']['citation_rate']

            # Alert: Significant citation rate drop (>10 percentage points)
            rate_drop = prev_rate - current_rate
            if rate_drop > 10:
                alert = self._create_alert(
                    db_session=db_session,
                    alert_type='citation_drop',
                    severity='high' if rate_drop > 20 else 'medium',
                    title=f'Citation rate dropped {rate_drop:.1f}pp in the last 7 days',
                    message=(
                        f"Brand citation rate dropped from {prev_rate:.1f}% to {current_rate:.1f}% "
                        f"(a {rate_drop:.1f} percentage point decline). Investigate content changes "
                        f"and competitor activity that may have caused this decline."
                    ),
                    metric_name='citation_rate',
                    previous_value=prev_rate,
                    current_value=current_rate,
                    threshold_value=10.0,
                    change_percentage=-rate_drop,
                )
                new_alerts.append(alert)

            # Alert: Competitor gaining citations significantly
            current_comp = current_summary.get('competitor_comparison', {})
            for comp_name, comp_data in current_comp.items():
                if comp_data['citation_rate'] > current_rate + 20:
                    alert = self._create_alert(
                        db_session=db_session,
                        alert_type='competitor_gain',
                        severity='medium',
                        title=f'{comp_name} citation rate exceeds brand by {comp_data["citation_rate"] - current_rate:.1f}pp',
                        message=(
                            f"Competitor {comp_name} has a citation rate of "
                            f"{comp_data['citation_rate']}% vs brand rate of {current_rate:.1f}%. "
                            f"Analyze their content strategy to identify why they are being cited more."
                        ),
                        metric_name='competitor_citation_rate',
                        previous_value=current_rate,
                        current_value=comp_data['citation_rate'],
                        competitor_name=comp_name,
                    )
                    new_alerts.append(alert)

            # Alert: Citation rate below critical threshold
            if current_rate < 20 and current_summary['overview']['total_queries'] >= 10:
                alert = self._create_alert(
                    db_session=db_session,
                    alert_type='threshold_breach',
                    severity='high',
                    title=f'Citation rate critically low: {current_rate:.1f}%',
                    message=(
                        f"Brand citation rate is {current_rate:.1f}%, well below the 20% minimum "
                        f"threshold. Immediate action needed to improve content authority and "
                        f"AI assistant visibility."
                    ),
                    metric_name='citation_rate',
                    current_value=current_rate,
                    threshold_value=20.0,
                )
                new_alerts.append(alert)

            self.logger.info(f"Alert check complete: {len(new_alerts)} new alerts created")
            return new_alerts

        except Exception as e:
            error_msg = f"Error checking citation alerts: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(self.agent_name, "", error_msg)
        finally:
            if not session_provided and db_session:
                db_session.close()

    def _create_alert(
        self,
        db_session: Session,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        metric_name: Optional[str] = None,
        previous_value: Optional[float] = None,
        current_value: Optional[float] = None,
        threshold_value: Optional[float] = None,
        change_percentage: Optional[float] = None,
        competitor_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create and persist an alert record

        Args:
            db_session: Database session
            alert_type: Type of alert
            severity: Alert severity
            title: Alert title
            message: Alert message
            metric_name: Name of metric that triggered alert
            previous_value: Previous metric value
            current_value: Current metric value
            threshold_value: Threshold that was breached
            change_percentage: Percentage change
            competitor_name: Competitor name (for competitor alerts)

        Returns:
            Alert dictionary
        """
        alert = AlertRecord(
            alert_type=alert_type,
            alert_severity=severity,
            status='active',
            title=title,
            message=message,
            brand_name=self.brand_name,
            competitor_name=competitor_name,
            metric_name=metric_name,
            previous_value=previous_value,
            current_value=current_value,
            threshold_value=threshold_value,
            change_percentage=change_percentage,
            triggered_at=datetime.utcnow(),
        )
        db_session.add(alert)
        db_session.commit()

        self.logger.info(f"Alert created: [{severity}] {title}")

        return {
            'id': alert.id,
            'type': alert_type,
            'severity': severity,
            'title': title,
            'message': message,
            'triggered_at': alert.triggered_at.isoformat(),
        }

    def generate_tracking_report(
        self,
        days: int = 30,
        include_competitor_analysis: bool = True,
        db_session: Optional[Session] = None,
    ) -> tuple[str, Path]:
        """
        Generate a comprehensive citation tracking report using AI analysis

        Combines data from citation records with AI-generated insights to produce
        a detailed markdown report.

        Args:
            days: Number of days to cover
            include_competitor_analysis: Whether to include competitor section
            db_session: Optional database session

        Returns:
            Tuple of (report_content, file_path)
        """
        self.logger.info(f"Generating citation tracking report: days={days}")

        session_provided = db_session is not None
        if not session_provided:
            db_session = get_db_session()

        try:
            summary = self.get_citation_summary(days=days, db_session=db_session)
            gaps = self.identify_citation_gaps(days=days, db_session=db_session)

            # Build report context
            overview = summary['overview']
            platform_breakdown = "\n".join(
                f"  - {plat.title()}: {data['citation_rate']}% ({data['cited']}/{data['total_queries']} queries)"
                for plat, data in summary['by_platform'].items()
            )

            top_gaps = "\n".join(
                f"  - \"{gap['query']}\" (opportunity: {gap['opportunity_score']}, "
                f"competitors: {', '.join(gap['competitors_cited'][:3])})"
                for gap in gaps[:5]
            )

            competitor_section = ""
            if include_competitor_analysis:
                comp_lines = []
                for comp, data in summary.get('competitor_comparison', {}).items():
                    comp_lines.append(
                        f"  - {comp}: {data['citation_rate']}% citation rate"
                    )
                if comp_lines:
                    competitor_section = f"""
COMPETITOR CITATION RATES:
{chr(10).join(comp_lines)}"""

            prompt = f"""Generate a comprehensive citation tracking report for {BRAND_NAME}.

DATA SUMMARY:
- Time Period: Last {days} days
- Total Queries Monitored: {overview['total_queries']}
- Brand Citation Rate: {overview['citation_rate']}%
- Recommended Rate: {overview.get('recommended_count', 0)} times
- Trend: {overview['trend_direction']} ({overview['trend_change']:+.1f}pp vs previous period)

PLATFORM BREAKDOWN:
{platform_breakdown}

TOP CITATION GAPS (brand not cited, competitors are):
{top_gaps or '  No significant gaps identified'}
{competitor_section}

PROVIDE:
1. **Executive Summary**: 3-4 sentences on overall citation health
2. **Key Metrics Dashboard**: Clean presentation of the numbers
3. **Platform Performance**: Analysis of each AI platform's citation behavior
4. **Gap Analysis**: Top opportunities with specific actions
5. **Competitor Landscape**: How competitors compare (if data available)
6. **Trend Analysis**: What the trend means and where it's heading
7. **Priority Actions**: Top 5 prioritized next steps
8. **30-Day Forecast**: Expected trajectory based on current data

Format as a professional report in markdown with clear sections and actionable insights."""

            system_context = """You are a citation analytics expert generating reports for
an ecommerce brand's AEO (Answer Engine Optimization) program. Your reports should be:
- Data-driven with specific numbers and percentages
- Actionable with clear next steps
- Concise but comprehensive
- Written for marketing leadership audience
- Focused on business impact and ROI"""

            report_content, report_path = self.generate_and_save(
                prompt=prompt,
                output_dir=AEO_OUTPUT_DIR,
                system_context=system_context,
                filename=f"citation_tracking_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                metadata={
                    'type': 'citation_tracking_report',
                    'days': days,
                    'citation_rate': overview['citation_rate'],
                    'trend': overview['trend_direction'],
                    'total_queries': overview['total_queries'],
                },
                max_tokens=4096,
            )

            self.logger.info(f"Citation tracking report saved to: {report_path}")
            return report_content, report_path

        except Exception as e:
            error_msg = f"Error generating tracking report: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(self.agent_name, "", error_msg)
        finally:
            if not session_provided and db_session:
                db_session.close()

    def record_tracking_result(
        self,
        platform: str,
        query: str,
        brand_mentioned: bool,
        response_text: Optional[str] = None,
        citation_url: Optional[str] = None,
        citation_context: Optional[str] = None,
        competitor_citations: Optional[Dict[str, bool]] = None,
        opportunity_score: int = 0,
        response_time_ms: Optional[int] = None,
        query_category: Optional[str] = None,
        batch_id: Optional[str] = None,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Record a single automated citation tracking result to the CitationTracking table

        This method stores results from automated monitoring runs using the new
        CitationTracking schema designed for batch/automated tracking workflows.

        Args:
            platform: AI platform queried (chatgpt, perplexity, claude, google_ai)
            query: The query sent to the AI platform
            brand_mentioned: Whether the brand was mentioned
            response_text: Full response text
            citation_url: URL cited by the AI platform
            citation_context: Text snippet around brand mention
            competitor_citations: Dict of {competitor_name: was_mentioned}
            opportunity_score: Calculated opportunity score (0-100)
            response_time_ms: Response latency in milliseconds
            query_category: Category of query
            batch_id: Identifier for grouping queries in a monitoring run
            db_session: Optional database session

        Returns:
            Dictionary with the created tracking record details
        """
        self.logger.info(
            f"Recording tracking result: platform={platform}, query='{query[:60]}...', "
            f"mentioned={brand_mentioned}"
        )

        session_provided = db_session is not None
        if not session_provided:
            db_session = get_db_session()

        try:
            tracking_id = str(uuid.uuid4())[:50]

            record = CitationTracking(
                tracking_id=tracking_id,
                batch_id=batch_id,
                platform=platform.lower(),
                query=query,
                query_category=query_category,
                brand_mentioned=brand_mentioned,
                citation_url=citation_url,
                citation_context=citation_context,
                competitor_citations=json.dumps(competitor_citations) if competitor_citations else None,
                opportunity_score=max(0, min(opportunity_score, 100)),
                response_text=response_text,
                response_time_ms=response_time_ms,
            )
            db_session.add(record)
            db_session.commit()

            self.logger.info(f"Tracking result recorded: tracking_id={tracking_id}")

            return {
                'tracking_id': tracking_id,
                'platform': platform.lower(),
                'query': query,
                'brand_mentioned': brand_mentioned,
                'opportunity_score': opportunity_score,
                'batch_id': batch_id,
            }

        except Exception as e:
            db_session.rollback()
            error_msg = f"Error recording tracking result: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(self.agent_name, "", error_msg)
        finally:
            if not session_provided and db_session:
                db_session.close()

    def get_tracking_history(
        self,
        days: int = 30,
        platform: Optional[str] = None,
        batch_id: Optional[str] = None,
        db_session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Get automated tracking history from the CitationTracking table

        Provides a summary of automated monitoring runs including citation rates,
        opportunity scores, and platform breakdowns.

        Args:
            days: Number of days to look back
            platform: Optional platform filter
            batch_id: Optional batch filter
            db_session: Optional database session

        Returns:
            Dictionary with tracking history summary and records
        """
        self.logger.info(f"Fetching tracking history: days={days}, platform={platform or 'all'}")

        session_provided = db_session is not None
        if not session_provided:
            db_session = get_db_session()

        try:
            start_date = datetime.utcnow() - timedelta(days=days)

            query = db_session.query(CitationTracking).filter(
                CitationTracking.created_at >= start_date,
            )
            if platform:
                query = query.filter(CitationTracking.platform == platform.lower())
            if batch_id:
                query = query.filter(CitationTracking.batch_id == batch_id)

            records = query.order_by(CitationTracking.created_at.desc()).all()

            total = len(records)
            cited = sum(1 for r in records if r.brand_mentioned)
            citation_rate = (cited / total * 100) if total > 0 else 0

            # Average opportunity score for uncited queries
            uncited = [r for r in records if not r.brand_mentioned and r.opportunity_score]
            avg_opportunity = (
                sum(r.opportunity_score for r in uncited) / len(uncited)
                if uncited else 0
            )

            # Platform breakdown
            platforms = {}
            for r in records:
                if r.platform not in platforms:
                    platforms[r.platform] = {'total': 0, 'cited': 0}
                platforms[r.platform]['total'] += 1
                if r.brand_mentioned:
                    platforms[r.platform]['cited'] += 1

            for plat_data in platforms.values():
                plat_data['citation_rate'] = round(
                    plat_data['cited'] / plat_data['total'] * 100, 1
                ) if plat_data['total'] > 0 else 0

            # Batch summary
            batches = {}
            for r in records:
                if r.batch_id:
                    if r.batch_id not in batches:
                        batches[r.batch_id] = {'total': 0, 'cited': 0, 'date': r.created_at}
                    batches[r.batch_id]['total'] += 1
                    if r.brand_mentioned:
                        batches[r.batch_id]['cited'] += 1

            result = {
                'summary': {
                    'total_tracked': total,
                    'cited': cited,
                    'citation_rate': round(citation_rate, 1),
                    'avg_opportunity_score': round(avg_opportunity, 1),
                    'time_period_days': days,
                },
                'by_platform': platforms,
                'batches': {
                    bid: {
                        'total': data['total'],
                        'cited': data['cited'],
                        'citation_rate': round(data['cited'] / data['total'] * 100, 1),
                        'date': data['date'].isoformat() if data['date'] else None,
                    }
                    for bid, data in batches.items()
                },
            }

            self.logger.info(
                f"Tracking history: {total} records, {citation_rate:.1f}% citation rate"
            )

            return result

        except Exception as e:
            error_msg = f"Error fetching tracking history: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ContentGenerationError(self.agent_name, "", error_msg)
        finally:
            if not session_provided and db_session:
                db_session.close()
