#!/bin/bash
cd ai-content-agents
source venv/bin/activate
exec python -c "from database.models import ContentHistory, APIUsage; print('OK')" 2>&1 | tail -1
