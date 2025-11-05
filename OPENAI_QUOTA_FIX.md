# OpenAI Quota Issue - Complete Guide

## The Problem

Your AI assistant is failing because you've exceeded OpenAI API quota. Here's what's happening:

### Where OpenAI API is Being Called

1. **Embeddings (text-embedding-ada-002)** - Most expensive
   - RAG system converting product descriptions to vectors
   - Celery background task regenerating embeddings periodically
   - Every user query generates an embedding for semantic search
   - **Cost**: ~$0.0001 per 1K tokens (adds up quickly with many products)

2. **Chat Completions (GPT-4/GPT-4o-mini)** - Per conversation
   - Each AI chat message
   - Agent tool calls
   - **Cost**: GPT-4: $0.03/1K input tokens, GPT-4o-mini: $0.00015/1K

3. **Background Jobs** - Silent killers
   - Celery worker constantly retrying failed embedding calls
   - Look at your logs: "Retrying request to /embeddings" dozens of times

### Why You're Exceeding Quota

**Most Likely Reasons:**
- ✅ Free tier expired ($5 credit exhausted)
- ✅ Pay-as-you-go account with $0 balance
- ✅ Celery keeps retrying embeddings infinitely
- ✅ RAG system rebuilds index frequently

## Solution Options

### Option 1: Add OpenAI Credits (Recommended for Production)

**If you want the full AI experience:**

1. Go to https://platform.openai.com/settings/organization/billing
2. Add payment method
3. Add $10-20 credit (should last weeks for development)
4. Restart Docker: `docker compose restart`

**Estimated costs for development:**
- Light testing: $1-2/day
- Heavy development: $5-10/day
- Production (100 users/day): $50-100/month

---

### Option 2: Use Free Tier OpenAI Alternative (BEST for Testing)

Replace OpenAI with a free model:

**Ollama (Local, 100% Free):**
```bash
# Install Ollama
brew install ollama  # Mac
# OR
curl -fsSL https://ollama.com/install.sh | sh  # Linux

# Pull a model
ollama pull llama3.2:latest

# Update settings.py to use Ollama
# Change OPENAI_API_KEY requirement to optional
```

**Update agent_service.py:**
```python
from langchain_community.llms import Ollama

# Instead of:
self.llm = ChatOpenAI(model="gpt-4o-mini", ...)

# Use:
self.llm = Ollama(model="llama3.2")
```

**Pros:**
- ✅ 100% free
- ✅ No API limits
- ✅ Runs locally
- ✅ Fast responses

**Cons:**
- ❌ Need to install Ollama
- ❌ Slightly less accurate than GPT-4
- ❌ Requires 8GB+ RAM

---

### Option 3: Disable AI Entirely (Quickest Fix for Now)

**To test Phase 4 checkout WITHOUT AI:**

You can manually add items to cart via the regular UI, then use direct API calls to test checkout:

```bash
# Add product to cart manually in UI
# Then run checkout test script
cd server
chmod +x test_phase4_quick.sh
./test_phase4_quick.sh
```

This tests the checkout API endpoints without needing the AI chat.

---

### Option 4: Remove RAG, Keep Basic AI (Current Attempt)

**What I already did:**
- ✅ Wrapped RAG in try-catch to skip embeddings
- ✅ Agent still uses tools for checkout
- ❌ But agent initialization itself is failing

**Problem:** The agent service file has caching issues. Let me try one more fix:

---

## Immediate Fix: Disable Agent Temporarily

Since the agent keeps failing, let's make the chat endpoint work without it:

**Edit `/server/apps/ai_assistant/views.py`:**
```python
# Around line 89-97, wrap agent call:
try:
    agent_service = get_agent_service()
    ai_response = agent_service.generate_response(...)
except Exception as e:
    # Fallback: simple response without AI
    ai_response = {
        "content": "AI assistant temporarily unavailable. For checkout, please use the cart page or contact support.",
        "metadata": {"error": str(e)[:200]}
    }
```

This allows the UI to load without crashing, even if AI fails.

---

## Long-Term Fixes

### 1. Reduce OpenAI Costs

**In `server/apps/ai_assistant/services/agent_service.py`:**
```python
# Use cheaper model
self.llm = ChatOpenAI(
    model="gpt-4o-mini",  # ✅ Already doing this
    temperature=0.7,
    max_tokens=500,  # ✅ Add this to limit response length
)
```

### 2. Disable Celery Embedding Tasks

**Comment out in `server/apps/ai_assistant/tasks.py`:**
```python
# @shared_task
# def update_index():
#     """Periodically update the AI index"""
#     # ... disabled to save API costs
```

### 3. Cache Embeddings Better

Don't regenerate embeddings on every Docker restart.

### 4. Rate Limit AI Requests

Add rate limiting per user to prevent abuse.

---

## Testing Phase 4 Without Fixing OpenAI

You can test checkout flow WITHOUT the AI assistant:

### Manual Cart + API Testing

1. **Add items to cart manually:**
   - Go to product page
   - Click "Add to Cart"
   - Cart badge updates

2. **Test checkout via test script:**
```bash
cd server
./test_phase4_quick.sh
```

3. **Or test via Postman/curl:**
```bash
SESSION_ID="test-$(date +%s)"

# Add to cart
curl -X POST http://localhost:8000/api/ai-assistant/cart/add/ \
  -H "Content-Type: application/json" \
  -d '{"session_id":"'$SESSION_ID'", "product_id":1, "name":"Test", "price":50000, "quantity":2}'

# Initiate checkout
curl -X POST http://localhost:8000/api/ai-assistant/checkout/initiate/ \
  -H "Content-Type: application/json" \
  -d '{"session_id":"'$SESSION_ID'"}'

# Continue with address, shipping, payment...
```

This tests that Phase 4 **backend and API work** without needing the AI chat to work.

---

## My Recommendation

**For RIGHT NOW (next 10 minutes):**
1. Test Phase 4 using the test script (no AI needed)
2. Verify checkout API endpoints work
3. Check orders are created in database

**For NEXT SESSION:**
1. Either:
   - Add $10 OpenAI credit (easiest)
   - OR install Ollama (free, local AI)
   - OR disable AI chat feature entirely

**Don't fight the AI agent right now** - focus on verifying Phase 4 checkout logic works via direct API testing.

---

## Current Status

- ✅ Docker containers running
- ✅ Backend API healthy
- ✅ Cart endpoints working
- ✅ Checkout endpoints created
- ❌ AI chat broken (OpenAI quota)
- ❌ Agent service cached/not loading new code

**Next Step:** Test checkout WITHOUT AI using the test script I provided earlier.

---

## Quick Test Command

```bash
cd /Users/kauutla/work/marcus-eccommerce/server
chmod +x test_phase4_quick.sh
./test_phase4_quick.sh
```

This will show you if Phase 4 checkout **actually works**, independent of the AI chat issue.
