# AEO End-to-End Verification Guide

## Overview

This guide provides comprehensive steps to verify the AEO (Agentic Engine Optimization) implementation is working correctly from end to end.

**Date:** February 26, 2026
**Feature:** AEO Implementation
**Task:** subtask-7-1 - End-to-end AEO workflow verification

## Prerequisites

- Python 3.x installed
- All dependencies installed (`pip install -r requirements.txt`)
- Anthropic API key configured in `.env` file
- FastAPI server running

## Automated Verification

### Quick Start

Run the automated verification script:

```bash
python e2e_aeo_verification.py
```

This script will:
- ✓ Check all required files exist
- ✓ Verify AEOAgent implementation
- ✓ Verify API routes are defined
- ✓ Check database schema and migrations
- ✓ Verify test coverage
- ✓ Test API endpoints (if server is running)
- ✓ Verify AEO checklist implementation
- ✓ Verify AI testing workflow
- ✓ Check output directory configuration

Results are saved to `aeo_verification_results.json`.

## Manual Verification Steps

### Step 1: File Structure Verification

Verify all required files exist:

```bash
# Core AEO files
ls -l agents/aeo_agent.py
ls -l api/routes/aeo.py
ls -l api/models.py
ls -l aeo_checklist.py
ls -l aeo_testing_workflow.py

# Database files
ls -l database/models.py
ls -l database/migrations/002_aeo_citation_tracking.sql

# Test files
ls -l tests/test_aeo_agent.py
ls -l tests/test_api_aeo.py
```

**Expected Result:** All files should exist with recent modification dates.

### Step 2: Start FastAPI Server

Start the development server:

```bash
uvicorn api.main:app --reload --port 8000
```

**Expected Result:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Access API documentation at: http://localhost:8000/api/docs

### Step 3: Test AEO Health Endpoint

```bash
curl http://localhost:8000/api/aeo/health
```

**Expected Result:**
```json
{
  "status": "healthy",
  "service": "aeo",
  "timestamp": "2026-02-26T..."
}
```

### Step 4: Generate FAQ Content

Test FAQ content generation:

```bash
curl -X POST http://localhost:8000/api/aeo/generate-faq \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "TCG card storage and protection",
    "num_questions": 5,
    "target_audience": "collectors",
    "include_product_mentions": true
  }'
```

**Expected Result:**
- Status: 200 OK
- Response contains:
  - `request_id`: Unique identifier
  - `content`: FAQ content in markdown format
  - `file_path`: Path to saved file (e.g., `output/aeo/faq_*.md`)
  - `metadata`: Topic, question count, audience
  - `status`: "success"

**Verification:**
```bash
# Check that file was created
ls -lh output/aeo/faq_*.md

# View content
cat output/aeo/faq_*.md
```

### Step 5: Generate FAQ Schema

Test FAQ schema generation (JSON-LD):

```bash
curl -X POST http://localhost:8000/api/aeo/generate-faq-schema \
  -H "Content-Type: application/json" \
  -d '{
    "faq_items": [
      {
        "question": "What is the best way to store TCG cards?",
        "answer": "The Infinity Vault Premium Binder provides superior protection with acid-free pages and reinforced binding."
      },
      {
        "question": "How many cards can the binder hold?",
        "answer": "Our premium binders hold up to 360 cards in a compact, organized format."
      }
    ]
  }'
```

**Expected Result:**
- Status: 200 OK
- Response contains valid JSON-LD FAQPage schema
- Schema structure:
  ```json
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [...]
  }
  ```

**Verification:**
```bash
# Validate schema is proper JSON
curl -X POST http://localhost:8000/api/aeo/generate-faq-schema \
  -H "Content-Type: application/json" \
  -d '{"faq_items": [...]}' | python -m json.tool
```

### Step 6: Generate Product Schema

Test Product schema generation:

```bash
curl -X POST http://localhost:8000/api/aeo/generate-product-schema \
  -H "Content-Type: application/json" \
  -d '{
    "product_data": {
      "name": "Infinity Vault Premium TCG Binder",
      "description": "Professional-grade binder for trading card game collectors",
      "price": 49.99,
      "currency": "USD",
      "availability": "InStock",
      "rating": 4.8,
      "review_count": 127
    }
  }'
```

**Expected Result:**
- Status: 200 OK
- Response contains valid JSON-LD Product schema
- Schema includes: name, brand, offers, aggregateRating, etc.

### Step 7: Validate Content with AEO Checklist

Create test content file:

```bash
cat > test_content.md << 'EOF'
# Best TCG Binders for Card Protection

The Infinity Vault Premium Binder is the best choice for serious TCG collectors.

## Why Infinity Vault?

Our binders offer superior protection with:
- Acid-free pages
- Reinforced binding
- 360-card capacity
- Premium materials

## Frequently Asked Questions

**Q: How many cards fit in the binder?**
A: Each binder holds up to 360 standard-sized TCG cards.

**Q: Are the pages acid-free?**
A: Yes, all pages are 100% acid-free to prevent card damage.
EOF
```

Run AEO checklist validation:

```bash
python -c "
from aeo_checklist import AEOChecklist
from pathlib import Path

content = Path('test_content.md').read_text()
checklist = AEOChecklist()
result = checklist.validate_content(content)

print(f'Score: {result[\"score\"]}/100')
print(f'Passed: {result[\"passed\"]}')
print(f'Checks: {result[\"checks\"]}')
print(f'Recommendations: {result[\"recommendations\"]}')
"
```

**Expected Result:**
- Score: >= 60/100
- Passed: True
- Individual checks show results for:
  - Clear answer
  - Structured headers
  - FAQ format
  - Definitive language
  - Brand mentions
  - Quotability
  - Front-loaded content
  - Specifics

### Step 8: Run AI Testing Workflow

Generate test instructions:

```bash
python aeo_testing_workflow.py --query "best TCG binder" --assistant claude
```

**Expected Result:**
- Outputs detailed testing instructions
- Shows query to ask AI assistant
- Lists what to look for in response
- Provides recording template

Alternative - run programmatically:

```bash
python -c "
from aeo_testing_workflow import AEOTestingWorkflow

workflow = AEOTestingWorkflow()
instructions = workflow.generate_test_instructions(
    query='best TCG binder for collectors',
    ai_assistant='claude'
)
print(instructions)
"
```

### Step 9: Verify Output Directory Structure

Check that AEO output directory is created and configured:

```bash
# Check config
grep -n "AEO_OUTPUT_DIR" config/config.py

# Check output directory
ls -la output/

# After running FAQ generation, verify files are saved
ls -la output/aeo/
```

**Expected Result:**
- `AEO_OUTPUT_DIR` defined in config.py
- `output/aeo/` directory exists (created on first use)
- Generated files saved with timestamps

### Step 10: Verify Database Schema

Check citation tracking database schema:

```bash
# View migration file
cat database/migrations/002_aeo_citation_tracking.sql

# Check model definition
grep -A 20 "class AEOCitationTest" database/models.py
```

**Expected Result:**
- Migration creates `aeo_citation_tests` table
- Table includes fields:
  - test_id (primary key)
  - query, ai_assistant, query_category
  - brand_mentioned, brand_recommended, citation_position
  - response_text, response_metadata
  - test_date, tester_name, notes
- Model matches schema definition

### Step 11: Run Unit Tests

Run AEO agent unit tests:

```bash
pytest tests/test_aeo_agent.py -v
```

**Expected Result:**
- All tests pass
- Coverage includes:
  - AEOAgent initialization
  - FAQ content generation
  - FAQ schema generation
  - Product schema generation
  - AI-optimized content
  - Comparison content
  - Error handling

### Step 12: Run API Integration Tests

Run AEO API tests:

```bash
pytest tests/test_api_aeo.py -v
```

**Expected Result:**
- All tests pass
- Coverage includes:
  - FAQ generation endpoint
  - FAQ schema endpoint
  - Product schema endpoint
  - AI-optimized content endpoint
  - Comparison content endpoint
  - Health check endpoint
  - Request validation
  - Error handling

### Step 13: Run Full Test Suite

Run all tests to ensure no regressions:

```bash
pytest -v
```

**Expected Result:**
- All tests pass (including existing tests)
- No failures or errors
- Test coverage >= 80%

## Verification Checklist

Use this checklist to track verification progress:

- [ ] ✓ All required files exist
- [ ] ✓ AEOAgent class properly implements all methods
- [ ] ✓ API routes registered and accessible
- [ ] ✓ FastAPI server starts without errors
- [ ] ✓ Health endpoint returns 200 OK
- [ ] ✓ FAQ content generation works
- [ ] ✓ FAQ schema generation produces valid JSON-LD
- [ ] ✓ Product schema generation produces valid JSON-LD
- [ ] ✓ AI-optimized content generation works
- [ ] ✓ Comparison content generation works
- [ ] ✓ AEO checklist validates content correctly
- [ ] ✓ AI testing workflow generates instructions
- [ ] ✓ Output files saved to output/aeo/
- [ ] ✓ Database migration exists
- [ ] ✓ AEOCitationTest model defined
- [ ] ✓ Unit tests pass
- [ ] ✓ API integration tests pass
- [ ] ✓ Full test suite passes

## Success Criteria

The AEO implementation is considered complete when:

1. **All Files Present:** All required files exist and are properly structured
2. **Server Starts:** FastAPI server starts without errors
3. **Endpoints Work:** All 6 API endpoints return valid responses
4. **Schemas Valid:** Generated JSON-LD schemas validate against schema.org
5. **Tests Pass:** All unit and integration tests pass
6. **Checklist Works:** AEO checklist correctly validates content
7. **Workflow Ready:** AI testing workflow generates proper instructions
8. **Database Ready:** Citation tracking schema is in place
9. **No Regressions:** Existing functionality still works

## Troubleshooting

### Server Won't Start

```bash
# Check for port conflicts
lsof -i :8000

# Check for syntax errors
python -m py_compile api/main.py

# Check dependencies
pip install -r requirements.txt
```

### API Endpoints Return 500 Errors

```bash
# Check logs
tail -f logs/app.log

# Verify environment variables
cat .env

# Test agent directly
python -c "from agents.aeo_agent import AEOAgent; agent = AEOAgent()"
```

### Tests Failing

```bash
# Run with verbose output
pytest -vv --tb=long

# Run specific test
pytest tests/test_aeo_agent.py::test_name -v

# Check coverage
pytest --cov=agents.aeo_agent --cov-report=html
```

## Next Steps

After successful verification:

1. **Commit Changes:**
   ```bash
   git add .
   git commit -m "auto-claude: subtask-7-1 - End-to-end AEO workflow verification"
   ```

2. **Update Implementation Plan:**
   - Mark subtask-7-1 as completed
   - Update build-progress.txt

3. **Documentation:**
   - Update README with AEO features
   - Add API endpoint documentation

4. **Production Readiness:**
   - Review security considerations
   - Configure rate limiting
   - Set up monitoring

## Reference Documentation

- **AEO Strategy:** `../../02-agentic-engine-optimization/aeo-strategy-plan.md`
- **API Documentation:** http://localhost:8000/api/docs
- **Implementation Plan:** `.auto-claude/specs/010-aeo-agentic-engine-optimization-implementation/implementation_plan.json`

## Support

For issues or questions:
- Review the build-progress.txt file
- Check the implementation plan
- Consult the AEO strategy plan
- Review test files for usage examples
