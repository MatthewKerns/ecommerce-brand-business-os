#!/bin/bash
cd "$(dirname "$0")/ai-content-agents"

# Try to import all three API test modules
./venv/bin/python3 -c "
import sys
sys.path.insert(0, '.')

try:
    # Test that all API test modules can be imported
    import tests.test_api
    import tests.test_api_blog
    import tests.test_api_social

    # Count test classes in each module
    test_api_classes = len([name for name in dir(tests.test_api) if name.startswith('Test')])
    test_blog_classes = len([name for name in dir(tests.test_api_blog) if name.startswith('Test')])
    test_social_classes = len([name for name in dir(tests.test_api_social) if name.startswith('Test')])

    print(f'test_api.py: {test_api_classes} test classes')
    print(f'test_api_blog.py: {test_blog_classes} test classes')
    print(f'test_api_social.py: {test_social_classes} test classes')

    if test_api_classes > 0 and test_blog_classes > 0 and test_social_classes > 0:
        print('OK')
    else:
        print('FAIL: Missing test classes')
        sys.exit(1)

except Exception as e:
    print(f'FAIL: {e}')
    sys.exit(1)
" 2>&1 | tail -5
