#!/bin/bash

echo "Testing AI Chat API..."
echo ""

curl -X POST http://localhost:8000/api/ai-assistant/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "hello",
    "session_id": "test-'$(date +%s)'",
    "context": {}
  }' 2>&1

echo ""
echo ""
echo "Check Django logs for errors:"
echo "docker logs marcus-eccommerce-backend-web-1 2>&1 | tail -30"
