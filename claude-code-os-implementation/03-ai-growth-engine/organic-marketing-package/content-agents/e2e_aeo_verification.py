#!/usr/bin/env python3
"""
End-to-End AEO Workflow Verification Script

This script performs comprehensive verification of the AEO (Agentic Engine Optimization) implementation.
It tests all components including:
1. AEOAgent functionality
2. FAQ and Product schema generation
3. AEO checklist validation
4. API endpoints
5. Database schema
6. Output file generation
7. Citation tracking

Usage:
    python e2e_aeo_verification.py

Requirements:
    - FastAPI server must be running on localhost:8000
    - All dependencies must be installed
    - Database must be initialized
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import requests
from datetime import datetime

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

class AEOEndToEndVerification:
    """Comprehensive end-to-end verification for AEO implementation."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "timestamp": datetime.now().isoformat()
        }
        self.details = []

    def run_all_checks(self) -> bool:
        """Run all verification checks."""
        print_header("AEO End-to-End Verification")

        # Component checks
        self.check_file_structure()
        self.check_agent_implementation()
        self.check_api_routes()
        self.check_database_schema()
        self.check_test_coverage()

        # API endpoint checks (if server is running)
        if self.check_server_health():
            self.test_faq_generation_endpoint()
            self.test_faq_schema_endpoint()
            self.test_product_schema_endpoint()
            self.test_ai_optimized_content_endpoint()
            self.test_comparison_content_endpoint()
        else:
            print_warning("API server not running - skipping endpoint tests")
            print_info("Start server with: uvicorn api.main:app --reload")

        # Workflow checks
        self.check_aeo_checklist()
        self.check_testing_workflow()
        self.check_output_directories()

        # Print summary
        self.print_summary()

        return self.results["failed"] == 0

    def check_file_structure(self):
        """Verify all required files exist."""
        print_header("File Structure Verification")

        required_files = [
            "agents/aeo_agent.py",
            "api/routes/aeo.py",
            "api/models.py",
            "database/models.py",
            "database/migrations/002_aeo_citation_tracking.sql",
            "tests/test_aeo_agent.py",
            "tests/test_api_aeo.py",
            "aeo_checklist.py",
            "aeo_testing_workflow.py",
            "config/config.py"
        ]

        for file_path in required_files:
            path = Path(file_path)
            self.results["total_checks"] += 1
            if path.exists():
                print_success(f"Found: {file_path}")
                self.results["passed"] += 1
            else:
                print_error(f"Missing: {file_path}")
                self.results["failed"] += 1
                self.details.append(f"Missing file: {file_path}")

    def check_agent_implementation(self):
        """Verify AEOAgent implementation."""
        print_header("AEO Agent Implementation")

        try:
            # Check if agent file has required methods
            agent_file = Path("agents/aeo_agent.py")
            if agent_file.exists():
                content = agent_file.read_text()

                required_methods = [
                    "generate_faq_content",
                    "generate_faq_schema",
                    "generate_product_schema",
                    "generate_ai_optimized_content",
                    "generate_comparison_content"
                ]

                for method in required_methods:
                    self.results["total_checks"] += 1
                    if f"def {method}" in content:
                        print_success(f"Method implemented: {method}")
                        self.results["passed"] += 1
                    else:
                        print_error(f"Method missing: {method}")
                        self.results["failed"] += 1
            else:
                print_error("AEOAgent file not found")
                self.results["total_checks"] += 1
                self.results["failed"] += 1
        except Exception as e:
            print_error(f"Error checking agent: {str(e)}")
            self.results["failed"] += 1

    def check_api_routes(self):
        """Verify API routes are defined."""
        print_header("API Routes Verification")

        try:
            routes_file = Path("api/routes/aeo.py")
            if routes_file.exists():
                content = routes_file.read_text()

                required_routes = [
                    "/generate-faq",
                    "/generate-faq-schema",
                    "/generate-product-schema",
                    "/generate-ai-content",
                    "/generate-comparison",
                    "/health"
                ]

                for route in required_routes:
                    self.results["total_checks"] += 1
                    if route in content:
                        print_success(f"Route defined: {route}")
                        self.results["passed"] += 1
                    else:
                        print_error(f"Route missing: {route}")
                        self.results["failed"] += 1
            else:
                print_error("API routes file not found")
                self.results["total_checks"] += 1
                self.results["failed"] += 1
        except Exception as e:
            print_error(f"Error checking routes: {str(e)}")
            self.results["failed"] += 1

    def check_database_schema(self):
        """Verify database schema and migration."""
        print_header("Database Schema Verification")

        # Check migration file
        migration_file = Path("database/migrations/002_aeo_citation_tracking.sql")
        self.results["total_checks"] += 1
        if migration_file.exists():
            content = migration_file.read_text()
            if "CREATE TABLE aeo_citation_tests" in content:
                print_success("Migration file exists with correct table creation")
                self.results["passed"] += 1
            else:
                print_error("Migration file missing table creation")
                self.results["failed"] += 1
        else:
            print_error("Migration file not found")
            self.results["failed"] += 1

        # Check model definition
        models_file = Path("database/models.py")
        self.results["total_checks"] += 1
        if models_file.exists():
            content = models_file.read_text()
            if "class AEOCitationTest" in content:
                print_success("AEOCitationTest model defined")
                self.results["passed"] += 1
            else:
                print_error("AEOCitationTest model not found")
                self.results["failed"] += 1
        else:
            print_error("Models file not found")
            self.results["failed"] += 1

    def check_test_coverage(self):
        """Verify test files exist."""
        print_header("Test Coverage Verification")

        test_files = {
            "tests/test_aeo_agent.py": "AEO Agent unit tests",
            "tests/test_api_aeo.py": "AEO API integration tests"
        }

        for file_path, description in test_files.items():
            self.results["total_checks"] += 1
            path = Path(file_path)
            if path.exists():
                # Count test functions
                content = path.read_text()
                test_count = content.count("def test_")
                print_success(f"{description}: {test_count} tests")
                self.results["passed"] += 1
            else:
                print_error(f"{description}: File not found")
                self.results["failed"] += 1

    def check_server_health(self) -> bool:
        """Check if API server is running."""
        print_header("API Server Health Check")

        try:
            response = requests.get(f"{self.base_url}/api/aeo/health", timeout=2)
            self.results["total_checks"] += 1
            if response.status_code == 200:
                print_success("API server is running")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"API server returned status {response.status_code}")
                self.results["failed"] += 1
                return False
        except requests.exceptions.RequestException as e:
            print_warning(f"API server not accessible: {str(e)}")
            self.results["total_checks"] += 1
            self.results["warnings"] += 1
            return False

    def test_faq_generation_endpoint(self):
        """Test FAQ generation endpoint."""
        print_header("FAQ Generation Endpoint Test")

        try:
            payload = {
                "topic": "TCG card storage",
                "num_questions": 5,
                "target_audience": "collectors",
                "include_product_mentions": True
            }

            response = requests.post(
                f"{self.base_url}/api/aeo/generate-faq",
                json=payload,
                timeout=30
            )

            self.results["total_checks"] += 1
            if response.status_code == 200:
                data = response.json()
                if "content" in data and "metadata" in data:
                    print_success("FAQ generation endpoint working")
                    print_info(f"Request ID: {data.get('request_id', 'N/A')}")
                    self.results["passed"] += 1
                else:
                    print_error("Response missing required fields")
                    self.results["failed"] += 1
            else:
                print_error(f"Endpoint returned status {response.status_code}")
                self.results["failed"] += 1
        except Exception as e:
            print_error(f"Error testing endpoint: {str(e)}")
            self.results["failed"] += 1

    def test_faq_schema_endpoint(self):
        """Test FAQ schema generation endpoint."""
        print_header("FAQ Schema Generation Endpoint Test")

        try:
            payload = {
                "faq_items": [
                    {
                        "question": "What is the best TCG binder?",
                        "answer": "The Infinity Vault Premium Binder offers superior protection."
                    }
                ]
            }

            response = requests.post(
                f"{self.base_url}/api/aeo/generate-faq-schema",
                json=payload,
                timeout=30
            )

            self.results["total_checks"] += 1
            if response.status_code == 200:
                data = response.json()
                if "schema" in data:
                    schema = json.loads(data["schema"])
                    if schema.get("@type") == "FAQPage":
                        print_success("FAQ schema endpoint working")
                        print_info(f"Schema type: {schema['@type']}")
                        self.results["passed"] += 1
                    else:
                        print_error("Invalid schema structure")
                        self.results["failed"] += 1
                else:
                    print_error("Response missing schema")
                    self.results["failed"] += 1
            else:
                print_error(f"Endpoint returned status {response.status_code}")
                self.results["failed"] += 1
        except Exception as e:
            print_error(f"Error testing endpoint: {str(e)}")
            self.results["failed"] += 1

    def test_product_schema_endpoint(self):
        """Test Product schema generation endpoint."""
        print_header("Product Schema Generation Endpoint Test")

        try:
            payload = {
                "product_data": {
                    "name": "Premium TCG Binder",
                    "description": "High-quality binder for TCG cards"
                }
            }

            response = requests.post(
                f"{self.base_url}/api/aeo/generate-product-schema",
                json=payload,
                timeout=30
            )

            self.results["total_checks"] += 1
            if response.status_code == 200:
                data = response.json()
                if "schema" in data:
                    schema = json.loads(data["schema"])
                    if schema.get("@type") == "Product":
                        print_success("Product schema endpoint working")
                        print_info(f"Product name: {schema.get('name', 'N/A')}")
                        self.results["passed"] += 1
                    else:
                        print_error("Invalid schema structure")
                        self.results["failed"] += 1
                else:
                    print_error("Response missing schema")
                    self.results["failed"] += 1
            else:
                print_error(f"Endpoint returned status {response.status_code}")
                self.results["failed"] += 1
        except Exception as e:
            print_error(f"Error testing endpoint: {str(e)}")
            self.results["failed"] += 1

    def test_ai_optimized_content_endpoint(self):
        """Test AI-optimized content generation endpoint."""
        print_header("AI-Optimized Content Endpoint Test")

        try:
            payload = {
                "question": "How to protect TCG cards?",
                "content_type": "answer",
                "include_sources": True
            }

            response = requests.post(
                f"{self.base_url}/api/aeo/generate-ai-content",
                json=payload,
                timeout=30
            )

            self.results["total_checks"] += 1
            if response.status_code == 200:
                data = response.json()
                if "content" in data:
                    print_success("AI-optimized content endpoint working")
                    self.results["passed"] += 1
                else:
                    print_error("Response missing content")
                    self.results["failed"] += 1
            else:
                print_error(f"Endpoint returned status {response.status_code}")
                self.results["failed"] += 1
        except Exception as e:
            print_error(f"Error testing endpoint: {str(e)}")
            self.results["failed"] += 1

    def test_comparison_content_endpoint(self):
        """Test comparison content generation endpoint."""
        print_header("Comparison Content Endpoint Test")

        try:
            payload = {
                "comparison_topic": "TCG storage solutions",
                "items_to_compare": ["Premium Binders", "Basic Binders", "Card Sleeves"],
                "include_recommendation": True
            }

            response = requests.post(
                f"{self.base_url}/api/aeo/generate-comparison",
                json=payload,
                timeout=30
            )

            self.results["total_checks"] += 1
            if response.status_code == 200:
                data = response.json()
                if "content" in data:
                    print_success("Comparison content endpoint working")
                    self.results["passed"] += 1
                else:
                    print_error("Response missing content")
                    self.results["failed"] += 1
            else:
                print_error(f"Endpoint returned status {response.status_code}")
                self.results["failed"] += 1
        except Exception as e:
            print_error(f"Error testing endpoint: {str(e)}")
            self.results["failed"] += 1

    def check_aeo_checklist(self):
        """Verify AEO checklist implementation."""
        print_header("AEO Checklist Verification")

        checklist_file = Path("aeo_checklist.py")
        self.results["total_checks"] += 1

        if checklist_file.exists():
            content = checklist_file.read_text()
            required_methods = [
                "validate_content",
                "check_clear_answer",
                "check_structured_headers",
                "check_faq_format"
            ]

            all_found = True
            for method in required_methods:
                if f"def {method}" not in content:
                    print_error(f"Missing method: {method}")
                    all_found = False

            if all_found:
                print_success("AEO checklist properly implemented")
                self.results["passed"] += 1
            else:
                print_error("AEO checklist missing methods")
                self.results["failed"] += 1
        else:
            print_error("AEO checklist file not found")
            self.results["failed"] += 1

    def check_testing_workflow(self):
        """Verify AI testing workflow implementation."""
        print_header("AI Testing Workflow Verification")

        workflow_file = Path("aeo_testing_workflow.py")
        self.results["total_checks"] += 1

        if workflow_file.exists():
            content = workflow_file.read_text()
            required_components = [
                "class AEOTestingWorkflow",
                "def generate_test_instructions",
                "def record_test_result",
                "def generate_citation_report"
            ]

            all_found = True
            for component in required_components:
                if component not in content:
                    print_error(f"Missing component: {component}")
                    all_found = False

            if all_found:
                print_success("AI testing workflow properly implemented")
                self.results["passed"] += 1
            else:
                print_error("AI testing workflow missing components")
                self.results["failed"] += 1
        else:
            print_error("AI testing workflow file not found")
            self.results["failed"] += 1

    def check_output_directories(self):
        """Verify output directories are properly configured."""
        print_header("Output Directory Verification")

        output_dir = Path("output")
        self.results["total_checks"] += 1

        if output_dir.exists():
            print_success("Output directory exists")

            # Check if AEO directory will be created
            config_file = Path("config/config.py")
            if config_file.exists():
                content = config_file.read_text()
                if "AEO_OUTPUT_DIR" in content:
                    print_success("AEO output directory configured")
                    self.results["passed"] += 1
                else:
                    print_error("AEO output directory not configured")
                    self.results["failed"] += 1
            else:
                print_error("Config file not found")
                self.results["failed"] += 1
        else:
            print_error("Output directory not found")
            self.results["failed"] += 1

    def print_summary(self):
        """Print verification summary."""
        print_header("Verification Summary")

        total = self.results["total_checks"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        warnings = self.results["warnings"]

        print(f"Total Checks: {total}")
        print_success(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        if failed > 0:
            print_error(f"Failed: {failed}/{total}")
        if warnings > 0:
            print_warning(f"Warnings: {warnings}")

        if failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All checks passed!{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ {failed} check(s) failed{Colors.RESET}")
            if self.details:
                print("\nFailure Details:")
                for detail in self.details:
                    print(f"  - {detail}")

        # Save results to file
        results_file = Path("aeo_verification_results.json")
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n{Colors.BLUE}Results saved to: {results_file}{Colors.RESET}")


def main():
    """Main entry point."""
    print(f"{Colors.BOLD}AEO End-to-End Verification Script{Colors.RESET}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Run verification
    verifier = AEOEndToEndVerification()
    success = verifier.run_all_checks()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
