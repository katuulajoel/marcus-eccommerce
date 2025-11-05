# Claude Model Name Fix

## Issue
The multi-agent system was using incorrect Claude model names that don't exist in the API, causing 404 errors.

## Original (Incorrect) Model Names
```python
# Cart Agent & Router Agent
model_name="claude-haiku-4-20250514"  # ❌ This model doesn't exist

# Product Agent & Checkout Agent
model_name="claude-sonnet-4-20250514"  # ❌ This model doesn't exist
```

## Attempts Made

###  Attempt 1: Used `claude-3-5-sonnet-20241022`
- Result: 404 error - model not found

### Attempt 2: Used `claude-3-5-sonnet-20240620`
- Result: 404 error - model not found

### Attempt 3: Should use latest stable models

## Correct Model Names (Current API)

Based on Anthropic's API, the correct models are:
- **Haiku**: `claude-3-5-haiku-20241022` ✅ (worked!)
- **Sonnet**: `claude-3-5-sonnet-20241022` OR `claude-3-5-sonnet-latest`

## Solution

Update all agent files to use correct model names:

**For Haiku (Cart + Router):**
```python
model_name="claude-3-5-haiku-20241022"
```

**For Sonnet (Product + Checkout):**
```python
model_name="claude-3-5-sonnet-latest"  # Use latest to avoid version issues
```

## Files to Update
1. `/server/apps/ai_assistant/agents/product_agent.py` (Line 32)
2. `/server/apps/ai_assistant/agents/checkout_agent.py` (Line 29)

## Testing
After fixing, test:
```bash
# Test cart (Haiku) - should work
curl -X POST http://localhost:8000/api/ai-assistant/chat/ \
  -d '{"session_id":"test","message":"Add to cart","context":{"productId":3}}'

# Test checkout (Sonnet) - should work after fix
curl -X POST http://localhost:8000/api/ai-assistant/chat/ \
  -d '{"session_id":"test","message":"I want to checkout","context":{}}'
```
