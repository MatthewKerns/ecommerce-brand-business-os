#!/usr/bin/env python3
"""Test script for FAQ schema generation"""
import sys
import os

# Add the content-agents directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents'))

import json
from agents.aeo_agent import AEOAgent

# Create agent
agent = AEOAgent()

# Test data
test_data = [
    {'question': 'Test?', 'answer': 'Test answer'}
]

# Generate schema
schema = agent.generate_faq_schema(test_data)

# Parse JSON
data = json.loads(schema)

# Verify structure
assert data['@type'] == 'FAQPage', f"Expected @type='FAQPage', got '{data.get('@type')}'"
assert '@context' in data, "Missing @context"
assert data['@context'] == 'https://schema.org', "Invalid @context"
assert 'mainEntity' in data, "Missing mainEntity"
assert len(data['mainEntity']) == 1, f"Expected 1 item, got {len(data['mainEntity'])}"
assert data['mainEntity'][0]['@type'] == 'Question', "Invalid Question type"
assert data['mainEntity'][0]['name'] == 'Test?', "Invalid question"
assert data['mainEntity'][0]['acceptedAnswer']['@type'] == 'Answer', "Invalid Answer type"
assert data['mainEntity'][0]['acceptedAnswer']['text'] == 'Test answer', "Invalid answer"

print('Valid FAQ Schema')
print('\nGenerated schema:')
print(json.dumps(data, indent=2))
