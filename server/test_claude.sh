#!/bin/bash
# Test Claude AI Chat API

curl -X POST http://localhost:8000/api/ai-assistant/chat/ \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"test-claude-123\", \"message\": \"Hello, what LLM are you using?\", \"context\": {}}"
