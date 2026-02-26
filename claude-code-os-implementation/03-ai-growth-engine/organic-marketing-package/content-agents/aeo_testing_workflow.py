"""
AEO Testing Workflow
Tests AI assistants (ChatGPT, Claude, Perplexity, etc.) with target queries
Tracks citation rates and brand mentions for Answer Engine Optimization
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from logging_config import get_logger
from config.config import AEO_OUTPUT_DIR


class AEOTestingWorkflow:
    """
    Workflow for testing AI assistant responses and tracking AEO performance
    Manages manual testing of target queries across multiple AI assistants
    """

    # AI assistants to test
    AI_ASSISTANTS = [
        "chatgpt",
        "claude",
        "perplexity",
        "gemini",
        "copilot"
    ]

    # Target query categories from AEO strategy
    QUERY_CATEGORIES = {
        "product_discovery": [
            "What's the best TCG binder?",
            "Best card binder for Pokemon",
            "Premium card storage solutions",
            "TCG storage products"
        ],
        "problem_solving": [
            "How to protect expensive trading cards",
            "Best way to organize a card collection",
            "How to store TCG cards safely"
        ],
        "comparison": [
            "Infinity Vault vs Vault X",
            "Best card binder brands comparison",
            "TCG binder comparison"
        ],
        "purchase_intent": [
            "What binder should I buy for tournament play?",
            "Gift for Pokemon card collector",
            "Best binder for competitive TCG players"
        ],
        "educational": [
            "How to prepare for a TCG tournament",
            "Card storage best practices",
            "Tournament preparation checklist"
        ]
    }

    def __init__(self):
        """Initialize the AEO testing workflow"""
        self.logger = get_logger("aeo_testing_workflow")
        self.test_results_dir = AEO_OUTPUT_DIR / "test_results"
        self.test_results_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("AEO Testing Workflow initialized")
        self.logger.debug(f"Test results directory: {self.test_results_dir}")

    def get_target_queries(
        self,
        category: Optional[str] = None
    ) -> List[str]:
        """
        Get list of target queries to test

        Args:
            category: Optional category filter (product_discovery, problem_solving, etc.)

        Returns:
            List of query strings
        """
        if category:
            if category not in self.QUERY_CATEGORIES:
                self.logger.warning(f"Unknown category: {category}")
                return []
            return self.QUERY_CATEGORIES[category]

        # Return all queries if no category specified
        all_queries = []
        for queries in self.QUERY_CATEGORIES.values():
            all_queries.extend(queries)
        return all_queries

    def generate_test_instructions(
        self,
        query: str,
        assistant: str = "chatgpt"
    ) -> Dict[str, Any]:
        """
        Generate manual testing instructions for a query/assistant pair

        Args:
            query: The query to test
            assistant: AI assistant to test (chatgpt, claude, perplexity, etc.)

        Returns:
            Dictionary with testing instructions and metadata
        """
        self.logger.info(f"Generating test instructions: query='{query}', assistant={assistant}")

        if assistant not in self.AI_ASSISTANTS:
            self.logger.warning(f"Unknown assistant: {assistant}")

        instructions = {
            "query": query,
            "assistant": assistant,
            "test_date": datetime.now().isoformat(),
            "instructions": self._build_instructions(query, assistant),
            "evaluation_criteria": {
                "brand_mentioned": "Is Infinity Vault mentioned in the response?",
                "position": "What position in the response? (1st, 2nd, 3rd, not mentioned)",
                "recommendation_type": "How is it mentioned? (recommended, mentioned, comparison, not mentioned)",
                "context": "What context? (positive, neutral, negative)",
                "quoted_content": "Did AI quote our content? (yes/no)",
                "cited_url": "Was our URL cited? (yes/no)"
            }
        }

        return instructions

    def _build_instructions(self, query: str, assistant: str) -> str:
        """Build detailed testing instructions string"""

        assistant_urls = {
            "chatgpt": "https://chat.openai.com",
            "claude": "https://claude.ai",
            "perplexity": "https://www.perplexity.ai",
            "gemini": "https://gemini.google.com",
            "copilot": "https://copilot.microsoft.com"
        }

        url = assistant_urls.get(assistant, "N/A")

        return f"""
MANUAL TEST INSTRUCTIONS
=========================

1. Open {assistant.title()} at: {url}

2. Enter the following query EXACTLY as written:
   "{query}"

3. Record the response by noting:
   - Is Infinity Vault mentioned? (YES/NO)
   - If yes, what position? (1st recommendation, 2nd, 3rd, or just mentioned)
   - How is it described? (Copy exact quote)
   - Is our website/content cited? (Note URL if yes)
   - Overall tone: Positive recommendation / Neutral mention / Negative

4. Screenshot the response and save as:
   {assistant}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png

5. Use the record_test_result() method to log findings

EVALUATION CHECKLIST:
✓ Brand mentioned (yes/no)
✓ Position in response (1st, 2nd, 3rd, not mentioned)
✓ Recommendation strength (strong/weak/neutral/none)
✓ Content quoted (yes/no)
✓ URL cited (yes/no)
✓ Overall sentiment (positive/neutral/negative)
"""

    def record_test_result(
        self,
        query: str,
        assistant: str,
        brand_mentioned: bool,
        position: Optional[str] = None,
        recommendation_type: Optional[str] = None,
        context: str = "neutral",
        quoted_content: bool = False,
        cited_url: bool = False,
        response_excerpt: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Path:
        """
        Record the results of a manual AEO test

        Args:
            query: The query tested
            assistant: AI assistant tested
            brand_mentioned: Whether Infinity Vault was mentioned
            position: Position in response (1st, 2nd, 3rd, not_mentioned)
            recommendation_type: How it was mentioned (recommended, mentioned, comparison, not_mentioned)
            context: Context of mention (positive, neutral, negative)
            quoted_content: Whether our content was quoted
            cited_url: Whether our URL was cited
            response_excerpt: Excerpt from the AI response (for analysis)
            notes: Additional notes

        Returns:
            Path to saved test result file
        """
        self.logger.info(f"Recording test result: query='{query}', assistant={assistant}, mentioned={brand_mentioned}")

        test_result = {
            "test_metadata": {
                "query": query,
                "assistant": assistant,
                "test_date": datetime.now().isoformat(),
                "tester": "manual"
            },
            "results": {
                "brand_mentioned": brand_mentioned,
                "position": position or "not_mentioned",
                "recommendation_type": recommendation_type or "not_mentioned",
                "context": context,
                "quoted_content": quoted_content,
                "cited_url": cited_url
            },
            "response_data": {
                "excerpt": response_excerpt or "",
                "notes": notes or ""
            },
            "aeo_metrics": {
                "citation_achieved": brand_mentioned and (quoted_content or cited_url),
                "recommendation_achieved": brand_mentioned and recommendation_type in ["recommended", "strong_recommended"],
                "positive_mention": brand_mentioned and context == "positive"
            }
        }

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_result_{assistant}_{timestamp}.json"
        result_path = self.test_results_dir / filename

        with open(result_path, 'w') as f:
            json.dump(test_result, f, indent=2)

        self.logger.info(f"Test result saved: {result_path}")
        return result_path

    def generate_citation_report(
        self,
        days: int = 30
    ) -> tuple[str, Path]:
        """
        Generate a citation rate report from recent test results

        Args:
            days: Number of days to include in report

        Returns:
            Tuple of (report_content, file_path)
        """
        self.logger.info(f"Generating citation report for last {days} days")

        # Load all test results
        test_files = list(self.test_results_dir.glob("test_result_*.json"))

        if not test_files:
            self.logger.warning("No test results found")
            report = "# AEO Citation Report\n\nNo test results found. Run some tests first!\n"
            report_path = self.test_results_dir / "citation_report_no_data.md"
            report_path.write_text(report)
            return report, report_path

        # Parse test results
        results = []
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)

        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    data = json.load(f)

                test_date = datetime.fromisoformat(data['test_metadata']['test_date'])
                if test_date.timestamp() >= cutoff_date:
                    results.append(data)
            except Exception as e:
                self.logger.error(f"Error loading test result {test_file}: {e}")

        # Generate report
        report = self._build_citation_report(results, days)

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.test_results_dir / f"citation_report_{timestamp}.md"
        report_path.write_text(report)

        self.logger.info(f"Citation report generated: {report_path}")
        return report, report_path

    def _build_citation_report(self, results: List[Dict], days: int) -> str:
        """Build citation report content from test results"""

        total_tests = len(results)
        if total_tests == 0:
            return "# AEO Citation Report\n\nNo test results in date range.\n"

        # Calculate metrics
        brand_mentions = sum(1 for r in results if r['results']['brand_mentioned'])
        citations = sum(1 for r in results if r['aeo_metrics']['citation_achieved'])
        recommendations = sum(1 for r in results if r['aeo_metrics']['recommendation_achieved'])
        positive_mentions = sum(1 for r in results if r['aeo_metrics']['positive_mention'])

        mention_rate = (brand_mentions / total_tests) * 100 if total_tests > 0 else 0
        citation_rate = (citations / total_tests) * 100 if total_tests > 0 else 0
        recommendation_rate = (recommendations / total_tests) * 100 if total_tests > 0 else 0

        # By assistant breakdown
        by_assistant = {}
        for result in results:
            assistant = result['test_metadata']['assistant']
            if assistant not in by_assistant:
                by_assistant[assistant] = {'total': 0, 'mentions': 0, 'citations': 0}
            by_assistant[assistant]['total'] += 1
            if result['results']['brand_mentioned']:
                by_assistant[assistant]['mentions'] += 1
            if result['aeo_metrics']['citation_achieved']:
                by_assistant[assistant]['citations'] += 1

        # Build report
        report = f"""# AEO Citation Report

**Report Period:** Last {days} days
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary Metrics

| Metric | Count | Rate |
|--------|-------|------|
| Total Tests | {total_tests} | 100% |
| Brand Mentions | {brand_mentions} | {mention_rate:.1f}% |
| Citations (quoted/cited) | {citations} | {citation_rate:.1f}% |
| Recommendations | {recommendations} | {recommendation_rate:.1f}% |
| Positive Mentions | {positive_mentions} | {(positive_mentions/total_tests)*100 if total_tests > 0 else 0:.1f}% |

## Performance by AI Assistant

| Assistant | Tests | Mentions | Citation Rate |
|-----------|-------|----------|---------------|
"""

        for assistant, data in sorted(by_assistant.items()):
            mention_pct = (data['mentions'] / data['total']) * 100 if data['total'] > 0 else 0
            citation_pct = (data['citations'] / data['total']) * 100 if data['total'] > 0 else 0
            report += f"| {assistant.title()} | {data['total']} | {data['mentions']} ({mention_pct:.1f}%) | {citation_pct:.1f}% |\n"

        # Add target analysis
        report += f"""

## Target Performance

**Current Performance vs Goals:**
- Brand Mention Rate: {mention_rate:.1f}% (Target: 60% at 6 months)
- Citation Rate: {citation_rate:.1f}% (Target: 40% at 6 months)
- Recommendation Rate: {recommendation_rate:.1f}% (Target: 40% at 6 months)

## Insights

"""

        if mention_rate >= 60:
            report += "✅ **Excellent!** Brand mention rate exceeds 6-month target.\n"
        elif mention_rate >= 25:
            report += "⚠️ **On Track** - Meeting 90-day target, continue optimizing for 6-month goal.\n"
        else:
            report += "❌ **Action Needed** - Brand mention rate below target. Increase content production and AEO optimization.\n"

        report += f"""

## Next Steps

1. Focus on query categories with low mention rates
2. Optimize content for AI assistant parsing
3. Build more FAQ schema and structured data
4. Continue weekly testing across all assistants
5. Track content that gets cited (analyze patterns)

---
*This report was generated automatically by AEO Testing Workflow*
"""

        return report

    def list_test_results(self) -> List[Dict[str, Any]]:
        """
        List all test results

        Returns:
            List of test result summaries
        """
        test_files = list(self.test_results_dir.glob("test_result_*.json"))

        results = []
        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    data = json.load(f)
                results.append({
                    "file": test_file.name,
                    "query": data['test_metadata']['query'],
                    "assistant": data['test_metadata']['assistant'],
                    "date": data['test_metadata']['test_date'],
                    "brand_mentioned": data['results']['brand_mentioned'],
                    "citation_achieved": data['aeo_metrics']['citation_achieved']
                })
            except Exception as e:
                self.logger.error(f"Error loading test result {test_file}: {e}")

        return sorted(results, key=lambda x: x['date'], reverse=True)
