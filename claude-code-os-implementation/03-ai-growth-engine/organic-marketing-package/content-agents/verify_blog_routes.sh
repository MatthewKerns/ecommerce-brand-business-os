#!/bin/bash
cd "$(dirname "$0")"
exec ./venv/bin/python3 -c "from api.routes.blog import router; print('OK')" 2>&1 | tail -1
