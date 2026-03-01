#!/usr/bin/env python3
"""
Simple verification script for BlogAgent.generate_meta_description
"""
import sys
from unittest.mock import Mock, patch

# Mock the Anthropic client before importing BlogAgent
with patch('agents.base_agent.anthropic.Anthropic') as mock_anthropic:
    # Create a mock client that returns a simulated meta description
    mock_client = Mock()
    mock_message = Mock()
    mock_message.content = [Mock(text="Master the art of testing with proven strategies for TCG players. Show up battle ready with expert tips.")]
    mock_client.messages.create.return_value = mock_message
    mock_anthropic.return_value = mock_client

    from agents.blog_agent import BlogAgent

    try:
        # Initialize agent
        agent = BlogAgent()

        # Generate meta description
        meta = agent.generate_meta_description('Article about testing')

        # Verify length
        if len(meta) <= 160:
            print('OK')
            print(f'Length: {len(meta)}')
            print(f'Meta: {meta}')
            sys.exit(0)
        else:
            print('FAIL')
            print(f'Length: {len(meta)} (expected <= 160)')
            print(f'Meta: {meta}')
            sys.exit(1)

    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
