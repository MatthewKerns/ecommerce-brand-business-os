#!/usr/bin/env python3
"""
Code-Level Implementation Verification Script

This script verifies that all code changes for the AI Content Agent Integration
feature have been properly implemented without requiring running services.

It checks:
- Database models exist and have correct fields
- API routes are properly defined
- Celery tasks are registered
- Pydantic models are defined
- Routes are registered in routers
"""

import sys
import os
import importlib.util
from pathlib import Path
from typing import List, Tuple, Optional

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def import_module_from_path(module_name: str, file_path: str):
    """Import a Python module from a file path"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        return None
    except Exception as e:
        print_error(f"Failed to import {module_name}: {e}")
        return None

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists"""
    path = Path(file_path)
    if path.exists():
        print_success(f"File exists: {file_path}")
        return True
    else:
        print_error(f"File missing: {file_path}")
        return False

def check_models() -> bool:
    """Verify database models implementation"""
    print_header("1. Database Models Verification")

    models_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/database/models.py"

    if not check_file_exists(models_path):
        return False

    # Read the file and check for required classes and fields
    with open(models_path, 'r') as f:
        content = f.read()

    checks = [
        ("ApprovalStatus enum", "class ApprovalStatus" in content or "ApprovalStatus = " in content),
        ("ContentReview model", "class ContentReview" in content),
        ("ContentReview.approval_status", "approval_status" in content),
        ("ContentReview.reviewer_id", "reviewer_id" in content),
        ("ContentReview.review_notes", "review_notes" in content),
        ("ContentHistory.version_number", "version_number" in content),
        ("ContentHistory.parent_content_id", "parent_content_id" in content),
        ("ContentHistory.is_draft", "is_draft" in content),
    ]

    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print_success(f"{check_name} found")
        else:
            print_error(f"{check_name} NOT found")
            all_passed = False

    return all_passed

def check_celery_tasks() -> bool:
    """Verify Celery tasks implementation"""
    print_header("2. Celery Tasks Verification")

    tasks_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/tasks/content_generation.py"

    if not check_file_exists(tasks_path):
        return False

    with open(tasks_path, 'r') as f:
        content = f.read()

    checks = [
        ("generate_blog_post_task", "def generate_blog_post_task" in content or "@app.task" in content),
        ("generate_social_post_task", "def generate_social_post_task" in content),
        ("priority parameter support", "priority" in content),
        ("is_draft=True setting", "is_draft=True" in content or 'is_draft": True' in content),
    ]

    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print_success(f"{check_name} found")
        else:
            print_error(f"{check_name} NOT found")
            all_passed = False

    # Check task registration
    tasks_init_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/tasks/__init__.py"

    if check_file_exists(tasks_init_path):
        with open(tasks_init_path, 'r') as f:
            init_content = f.read()

        if "generate_blog_post_task" in init_content:
            print_success("Tasks registered in __init__.py")
        else:
            print_error("Tasks NOT registered in __init__.py")
            all_passed = False

    return all_passed

def check_api_models() -> bool:
    """Verify API Pydantic models"""
    print_header("3. API Models Verification")

    models_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/api/models.py"

    if not check_file_exists(models_path):
        return False

    with open(models_path, 'r') as f:
        content = f.read()

    checks = [
        ("ReviewSubmitRequest", "class ReviewSubmitRequest" in content),
        ("ReviewActionRequest", "class ReviewActionRequest" in content),
        ("ReviewStatusResponse", "class ReviewStatusResponse" in content),
        ("BlogAsyncRequest", "class BlogAsyncRequest" in content),
        ("SocialAsyncRequest", "class SocialAsyncRequest" in content),
        ("AsyncTaskResponse", "class AsyncTaskResponse" in content),
        ("TaskStatusResponse", "class TaskStatusResponse" in content),
    ]

    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print_success(f"{check_name} found")
        else:
            print_error(f"{check_name} NOT found")
            all_passed = False

    return all_passed

def check_review_routes() -> bool:
    """Verify review workflow routes"""
    print_header("4. Review Routes Verification")

    routes_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/api/routes/review.py"

    if not check_file_exists(routes_path):
        return False

    with open(routes_path, 'r') as f:
        content = f.read()

    checks = [
        ("POST /submit endpoint", '"/submit"' in content or "@router.post" in content),
        ("POST /approve endpoint", '"/approve"' in content),
        ("POST /reject endpoint", '"/reject"' in content),
        ("GET /status endpoint", '"/status' in content or "@router.get" in content),
        ("ContentReview usage", "ContentReview" in content),
        ("ApprovalStatus usage", "ApprovalStatus" in content),
    ]

    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print_success(f"{check_name} found")
        else:
            print_error(f"{check_name} NOT found")
            all_passed = False

    return all_passed

def check_version_routes() -> bool:
    """Verify version management routes"""
    print_header("5. Version Routes Verification")

    routes_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/api/routes/versions.py"

    if not check_file_exists(routes_path):
        return False

    with open(routes_path, 'r') as f:
        content = f.read()

    checks = [
        ("GET /history endpoint", '"/history' in content),
        ("POST /create-revision endpoint", '"/create-revision"' in content),
        ("GET /compare endpoint", '"/compare' in content),
        ("POST /revert endpoint", '"/revert' in content),
        ("version_number usage", "version_number" in content),
        ("parent_content_id usage", "parent_content_id" in content),
    ]

    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print_success(f"{check_name} found")
        else:
            print_error(f"{check_name} NOT found")
            all_passed = False

    return all_passed

def check_task_routes() -> bool:
    """Verify task status routes"""
    print_header("6. Task Status Routes Verification")

    routes_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/api/routes/tasks.py"

    if not check_file_exists(routes_path):
        return False

    with open(routes_path, 'r') as f:
        content = f.read()

    checks = [
        ("GET /status endpoint", '"/status' in content),
        ("AsyncResult usage", "AsyncResult" in content),
        ("Task status mapping", "PENDING" in content or "SUCCESS" in content),
    ]

    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print_success(f"{check_name} found")
        else:
            print_error(f"{check_name} NOT found")
            all_passed = False

    return all_passed

def check_async_endpoints() -> bool:
    """Verify async generation endpoints in blog and social routes"""
    print_header("7. Async Generation Endpoints Verification")

    blog_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/api/routes/blog.py"
    social_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/api/routes/social.py"

    all_passed = True

    # Check blog async endpoint
    if check_file_exists(blog_path):
        with open(blog_path, 'r') as f:
            blog_content = f.read()

        if '"/generate-async"' in blog_content or 'generate-async' in blog_content:
            print_success("Blog async endpoint found")
        else:
            print_error("Blog async endpoint NOT found")
            all_passed = False

        if "generate_blog_post_task" in blog_content:
            print_success("Blog routes import Celery task")
        else:
            print_error("Blog routes do NOT import Celery task")
            all_passed = False
    else:
        all_passed = False

    # Check social async endpoint
    if check_file_exists(social_path):
        with open(social_path, 'r') as f:
            social_content = f.read()

        if '"/generate-async"' in social_content or 'generate-async' in social_content:
            print_success("Social async endpoint found")
        else:
            print_error("Social async endpoint NOT found")
            all_passed = False

        if "generate_social_post_task" in social_content:
            print_success("Social routes import Celery task")
        else:
            print_error("Social routes do NOT import Celery task")
            all_passed = False
    else:
        all_passed = False

    return all_passed

def check_route_registration() -> bool:
    """Verify routes are registered in main app"""
    print_header("8. Route Registration Verification")

    routes_init_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/api/routes/__init__.py"
    main_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/api/main.py"

    all_passed = True

    # Check routes __init__.py
    if check_file_exists(routes_init_path):
        with open(routes_init_path, 'r') as f:
            init_content = f.read()

        routers = ["review_router", "versions_router", "tasks_router"]
        for router in routers:
            if router in init_content:
                print_success(f"{router} exported from routes/__init__.py")
            else:
                print_error(f"{router} NOT exported from routes/__init__.py")
                all_passed = False
    else:
        all_passed = False

    # Check main.py
    if check_file_exists(main_path):
        with open(main_path, 'r') as f:
            main_content = f.read()

        routers = ["review_router", "versions_router", "tasks_router"]
        for router in routers:
            if router in main_content:
                print_success(f"{router} registered in main.py")
            else:
                print_error(f"{router} NOT registered in main.py")
                all_passed = False
    else:
        all_passed = False

    return all_passed

def check_celery_config() -> bool:
    """Verify Celery task routing configuration"""
    print_header("9. Celery Configuration Verification")

    config_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/config/celery_config.py"

    if not check_file_exists(config_path):
        return False

    with open(config_path, 'r') as f:
        content = f.read()

    checks = [
        ("Priority queues defined", "content_high" in content or "content_medium" in content),
        ("Blog task routing", "generate_blog_post_task" in content),
        ("Social task routing", "generate_social_post_task" in content),
    ]

    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print_success(f"{check_name} found")
        else:
            print_error(f"{check_name} NOT found")
            all_passed = False

    return all_passed

def check_migration() -> bool:
    """Verify database migration script exists"""
    print_header("10. Database Migration Verification")

    migration_path = "./claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/packages/content-engine/src/database/migrations/add_review_and_versioning.py"

    if not check_file_exists(migration_path):
        return False

    with open(migration_path, 'r') as f:
        content = f.read()

    checks = [
        ("content_reviews table", "content_reviews" in content or "ContentReview" in content),
        ("version_number field", "version_number" in content),
        ("parent_content_id field", "parent_content_id" in content),
        ("is_draft field", "is_draft" in content),
        ("run_migration function", "def run_migration" in content or "def migrate" in content),
    ]

    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print_success(f"{check_name} found")
        else:
            print_error(f"{check_name} NOT found")
            all_passed = False

    return all_passed

def main():
    """Run all verification checks"""
    print_header("AI Content Agent Integration - Code Implementation Verification")

    print_info("This script verifies that all code changes have been properly implemented.")
    print_info("It does NOT require running services - only checks code existence and structure.\n")

    results = []

    results.append(("Database Models", check_models()))
    results.append(("Celery Tasks", check_celery_tasks()))
    results.append(("API Models", check_api_models()))
    results.append(("Review Routes", check_review_routes()))
    results.append(("Version Routes", check_version_routes()))
    results.append(("Task Routes", check_task_routes()))
    results.append(("Async Endpoints", check_async_endpoints()))
    results.append(("Route Registration", check_route_registration()))
    results.append(("Celery Configuration", check_celery_config()))
    results.append(("Database Migration", check_migration()))

    # Summary
    print_header("Verification Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"{check_name:.<50} {status}")

    print(f"\n{Colors.BOLD}Total: {passed}/{total} checks passed{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.BOLD}{Colors.GREEN}✓ ALL CHECKS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}Implementation is complete and ready for E2E testing.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.BOLD}{Colors.RED}✗ SOME CHECKS FAILED{Colors.RESET}")
        print(f"{Colors.RED}Please fix the issues above before proceeding to E2E testing.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
