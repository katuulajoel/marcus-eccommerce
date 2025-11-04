# Phase 1 Testing Guide - Redis Cart & AI Tools

## Quick Start

### 1. Start Docker Services
```bash
cd server
docker compose up -d
```

### 2. Run Python Tests
```bash
# Test Redis cart service and LangChain tools
python test_cart_phase1.py
```

### 3. Run API Tests
```bash
# Test HTTP endpoints
./test_cart_api.sh
```

### 4. Manual Redis Inspection
```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# View all cart keys
KEYS cart:*

# Inspect a specific cart
HGETALL cart:session-xxx

# View cart items
SMEMBERS cart:session-xxx:items

# Check TTL (should be 604800 = 7 days)
TTL cart:session-xxx

# Clear test data
FLUSHDB
```

## Expected Results

### Python Tests Should Show:
- ✅ Redis connection successful
- ✅ Cart CRUD operations working
- ✅ TTL set to 7 days
- ✅ LangChain tools functional
- ✅ Multiple session ID formats work
- ✅ Redis key structure correct

### API Tests Should Show:
- ✅ POST /api/ai-assistant/cart/add/ - 200 OK
- ✅ GET /api/ai-assistant/cart/{session_id}/ - 200 OK
- ✅ POST /api/ai-assistant/cart/update-quantity/ - 200 OK
- ✅ POST /api/ai-assistant/cart/remove/ - 200 OK
- ✅ POST /api/ai-assistant/cart/clear/ - 200 OK

## Test AI Agent in Web UI

1. Start frontend:
```bash
npm run dev:client
```

2. Open browser: http://localhost:3000

3. Open AI Assistant panel

4. Test conversation:
```
You: "Show me balloon bouquets"
AI: [Shows products with search_products tool]

You: "I want 2 of the hot air balloon bouquets"
AI: [Uses add_to_cart tool]
    "✅ Added 2x Hot Air Balloon Bouquet to cart!
     Price: UGX 120,000 each = UGX 240,000
     Cart total: UGX 240,000
     Ready to checkout?"

You: "What's in my cart?"
AI: [Uses view_cart tool]
    "🛒 Your Shopping Cart (2 items):
     • 2x Hot Air Balloon Bouquet..."
```

## Troubleshooting

### Redis Connection Failed
```bash
# Check if Redis is running
docker compose ps redis

# Restart Redis
docker compose restart redis

# Check logs
docker compose logs redis
```

### Import Errors
```bash
# Reinstall dependencies
docker compose exec web pip install -r requirements.txt

# Rebuild containers
docker compose up --build
```

### Agent Not Using Tools
- Check OpenAI API key is set: `echo $OPENAI_API_KEY`
- Check agent verbose logs: `docker compose logs web | grep -i "tool"`
- Verify session_id is passed in context

## Next: Phase 2

Once all Phase 1 tests pass, proceed to Phase 2:
- Frontend action cards
- Cart context sync
- Real-time UI updates
