# Phase 3 Complete: Cart Context Sync with Backend

## Overview

Phase 3 migrates the cart from localStorage to full backend synchronization with Redis. All cart operations now go through the backend API, ensuring consistency between AI-added items and manually-added items.

## Changes Made

### 1. Cart Context Complete Refactor

**File:** `web/client/context/cart-context.tsx`

**Key Changes:**
- ✅ Removed all localStorage operations
- ✅ Made all cart operations async (return `Promise<void>`)
- ✅ Added automatic cart fetch when `sessionId` is available
- ✅ All operations now call backend API endpoints
- ✅ Added `refreshCart()` function for manual refresh
- ✅ Added `isLoading` state for better UX
- ✅ Transform backend cart format to frontend `CartItem` format

**Operations Now Calling Backend:**
```typescript
// All operations are now async and call API
addItem: (item: CartItem) => Promise<void>
removeItem: (id: string) => Promise<void>
updateQuantity: (id: string, quantity: number) => Promise<void>
clearCart: () => Promise<void>
refreshCart: () => Promise<void>  // NEW
```

**Automatic Sync:**
```typescript
// Fetch cart from backend when sessionId is available
useEffect(() => {
  if (sessionId) {
    fetchCart()
  }
}, [sessionId])
```

### 2. AI Action Card Auto-Refresh

**File:** `web/client/components/ai-assistant/ai-action-card.tsx`

**Key Changes:**
- ✅ Import `useCart` hook to access `refreshCart()`
- ✅ Added `useEffect` to trigger refresh when action cards display
- ✅ Automatically syncs cart when AI adds items

**Implementation:**
```typescript
const { refreshCart } = useCart()

// Refresh cart when action card is displayed (AI added items)
useEffect(() => {
  if (action.type === 'item_added' || action.type === 'cart_updated') {
    refreshCart()
  }
}, [action.type])
```

### 3. Complete Data Flow

```
User → AI Chat: "I want 2 balloon bouquets"
    ↓
AI Agent → LangChain add_to_cart tool
    ↓
Tool → Redis: cart:session-xxx:item:123 created
    ↓
Backend → Chat Response: includes action metadata
    ↓
Frontend → AIActionCard component renders
    ↓
useEffect → refreshCart() called
    ↓
Cart Context → fetchCart() from backend API
    ↓
UI Updates: Cart badge, Cart page, Action card
```

## Testing Phase 3

### Prerequisites

1. **Start Services:**
```bash
# Terminal 1: Backend
cd server
docker compose up --build

# Terminal 2: Frontend
npm run dev:client
```

2. **Verify Redis is Running:**
```bash
docker compose exec redis redis-cli ping
# Should return: PONG
```

### Test Scenario 1: AI Adds Items to Cart

**Goal:** Verify AI can autonomously add items and cart syncs

1. Open app at http://localhost:3000
2. Open AI Assistant panel
3. Type: "I want 2 balloon bouquets"
4. **Expected Results:**
   - ✅ AI responds with confirmation message
   - ✅ Green action card appears with item details
   - ✅ Cart badge updates to show "2" items
   - ✅ Action card shows correct price and totals
   - ✅ "View Cart" and "Checkout Now" buttons appear

5. Click "View Cart" button
6. **Expected Results:**
   - ✅ Navigate to `/cart` page
   - ✅ 2x Balloon Bouquets appear in cart
   - ✅ Correct prices displayed
   - ✅ Quantity controls work

### Test Scenario 2: Manual Add + AI View Cart

**Goal:** Verify AI can see manually-added items

1. Browse products and manually add 1 item to cart (e.g., click "Add to Cart" on any product)
2. **Expected Results:**
   - ✅ Cart badge increments
   - ✅ Item appears in Redis cart

3. Open AI Assistant
4. Type: "What's in my cart?"
5. **Expected Results:**
   - ✅ AI uses `view_cart` tool
   - ✅ AI lists all items (AI-added + manually-added)
   - ✅ AI shows correct totals

### Test Scenario 3: Cart Persistence Across Page Reload

**Goal:** Verify cart persists in Redis

1. Add items to cart (via AI or manually)
2. Note the cart badge count
3. Refresh the page (F5)
4. **Expected Results:**
   - ✅ Cart badge shows same count after reload
   - ✅ Cart page still shows all items
   - ✅ SessionId persists (check localStorage: `ai_session_id`)

### Test Scenario 4: Remove Items from Cart

**Goal:** Verify cart sync on removal

1. Add 3 items to cart
2. Open cart page
3. Click "Remove" on one item
4. **Expected Results:**
   - ✅ Item removed from cart
   - ✅ Cart badge decrements
   - ✅ Cart total updates
   - ✅ Redis cart updated

5. Ask AI: "What's in my cart now?"
6. **Expected Results:**
   - ✅ AI shows only 2 remaining items

### Test Scenario 5: Update Quantity

**Goal:** Verify quantity updates sync

1. Add item to cart
2. Open cart page
3. Increase quantity to 5
4. **Expected Results:**
   - ✅ Quantity updates in UI
   - ✅ Cart total recalculates
   - ✅ Cart badge updates to 5
   - ✅ Redis cart updated

5. Ask AI: "How much is my cart total?"
6. **Expected Results:**
   - ✅ AI shows correct total with 5x quantity

### Test Scenario 6: Clear Cart

**Goal:** Verify cart clearing works

1. Add multiple items to cart
2. Open cart page
3. Click "Clear Cart" button
4. **Expected Results:**
   - ✅ All items removed
   - ✅ Cart badge shows 0
   - ✅ Cart page shows empty state
   - ✅ Redis keys deleted

5. Ask AI: "What's in my cart?"
6. **Expected Results:**
   - ✅ AI responds "Your cart is empty"

## Troubleshooting

### Cart Badge Not Updating

**Issue:** AI adds items but cart badge doesn't update

**Fix:**
1. Check browser console for errors
2. Verify `refreshCart()` is being called in action card
3. Verify cart context is properly wrapping the app
4. Check Network tab for `/api/ai-assistant/cart/{sessionId}/` request

### Items Not Appearing in Cart Page

**Issue:** AI adds items but cart page is empty

**Check:**
1. Verify sessionId is consistent:
```javascript
localStorage.getItem('ai_session_id')
```

2. Check Redis cart:
```bash
docker compose exec redis redis-cli
> SELECT 1
> KEYS cart:*
> SMEMBERS cart:session-xxx:items
> HGETALL cart:session-xxx:item:123
```

3. Check cart API response:
```bash
curl http://localhost:8000/api/ai-assistant/cart/session-xxx/
```

### AI Can't See Manual Cart Items

**Issue:** Manually-added items don't appear when AI views cart

**Fix:**
1. Verify manual add is using same sessionId:
```typescript
const { sessionId } = useAIAssistant()
```

2. Check backend logs for errors during `addToCart()` call

3. Verify product_id is an integer (not string)

### Cart Items Have Wrong Format

**Issue:** Cart items missing images or configuration

**Fix:**
1. Check transformation in `cart-context.tsx`:
```typescript
const transformedItems: CartItem[] = cart.items.map((item: any) => ({
  id: item.item_id,
  name: item.name,
  price: item.price,
  image: item.image_url || '/placeholder.png',
  quantity: item.quantity,
  categoryId: item.category_id,
  configuration: item.configuration
}))
```

2. Ensure backend includes all fields in cart response

## Verification Checklist

Before moving to Phase 4, verify:

- [ ] AI can add items to cart autonomously
- [ ] Action cards appear with correct data
- [ ] Cart badge updates when items added/removed
- [ ] Cart page shows items from Redis backend
- [ ] Manual cart operations sync with backend
- [ ] AI can view and describe cart contents
- [ ] Cart persists across page reloads
- [ ] Cart TTL is set correctly (7 days)
- [ ] No localStorage cart operations remain
- [ ] No console errors during cart operations

## Redis Data Structure

**Cart Keys:**
```
cart:{session_id}                    # Hash: metadata (updated_at, customer_id)
cart:{session_id}:items              # Set: item IDs
cart:{session_id}:item:{item_id}     # Hash: item details
```

**Item Hash Fields:**
```
product_id: 123
name: "Balloon Bouquet"
price: "60000"
quantity: "2"
configuration: "{}"
image_url: "/images/balloons.jpg"
category_id: "5"
```

**TTL:**
All keys expire after 7 days (604800 seconds)

## What's Next?

Phase 3 is complete! The cart now fully syncs between:
- ✅ AI autonomous actions
- ✅ Manual user operations
- ✅ Frontend UI (badge, cart page, action cards)
- ✅ Backend Redis storage

**Ready for Phase 4: Checkout Flow**

Phase 4 will add:
- Checkout initialization tool for AI
- Address collection and validation
- Payment method selection
- Stripe payment link generation
- Mobile Money USSD integration
- Order creation (Redis cart → PostgreSQL order)

---

**Phase 3 Status:** ✅ Complete - Ready for Testing
