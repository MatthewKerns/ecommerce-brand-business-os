#!/bin/bash
cd "$(dirname "$0")/claude-code-os-implementation/03-ai-growth-engine/organic-marketing-package/content-agents"
exec ./venv/bin/python3 -c "
from api.routes.citation_monitoring import router
# Check that router exists
assert router is not None
# Check that there's a GET /citations endpoint
route_paths = [route.path for route in router.routes]
assert '/citations' in route_paths, f'GET /citations not found. Routes: {route_paths}'
# Find the route and check methods
for route in router.routes:
    if route.path == '/citations':
        assert 'GET' in route.methods, f'Expected GET method, got {route.methods}'
        break
print('✓ GET /citations endpoint verified successfully')
" 2>&1
