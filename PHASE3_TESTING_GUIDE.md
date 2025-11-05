# Phase 3 Testing Guide

## Quick Start Testing

### 1. Start Services

```bash
# Terminal 1: Backend
cd server
docker compose up --build

# Wait for services to be healthy
# You should see: "web-1 | Django version 4.2.x, using settings 'ecommerce_backend.settings'"
```

```bash
# Terminal 2: Frontend
cd /Users/kauutla/work/marcus-eccommerce
npm run dev:client

# Wait for Vite to start
# You should see: "Local:   http://localhost:3000/"
```

### 2. Quick Verification Test

**Open browser:** http://localhost:3000

**Step 1: Check cart badge is visible**
- Look at top-right corner of navigation
- Should see shopping cart icon (no badge yet - cart is empty)

**Step 2: AI adds item to cart**
1. Click AI Assistant button (bottom-right)
2. Type: "I want 2 balloon bouquets"
3. Press Enter

**Expected Results:**
- ✅ AI responds with confirmation
- ✅ **Green action card appears** with item details
- ✅ **Cart badge appears** with "2" (top-right navigation)
- ✅ Action card shows: "Added to Cart!" with item details
- ✅ Shows cart total in UGX

**Step 3: Verify cart persistence**
1. Click "View Cart" button on action card (OR click cart icon in navigation)
2. **Expected:** 2x Balloon Bouquets appear in cart page
3. Refresh the page (F5)
4. **Expected:** Cart still shows 2 items (persisted in Redis)

**If all above pass → Phase 3 is working!**

---

## Detailed Test Scenarios

### Scenario 1: AI Autonomous Cart Actions

**Test:** AI adds items without user clicking any buttons

1. Clear cart if not empty
2. Open AI Assistant
3. Try these prompts:

```
"I want 3 red roses"
"Add 5 chocolate boxes to my cart"
"I'll take 2 birthday cakes"
"Order 1 celebration balloon package"
```

**For each prompt, verify:**
- [ ] AI responds with confirmation (not just recommendation)
- [ ] Green action card appears
- [ ] Cart badge increments correctly
- [ ] Action card shows correct quantity and price
- [ ] "View Cart" and "Checkout Now" buttons work

**Check backend Redis:**
```bash
docker compose exec redis redis-cli
> SELECT 1
> KEYS cart:*
> SMEMBERS cart:session-{your-session-id}:items
> HGETALL cart:session-{your-session-id}:item:{item-id}
```

### Scenario 2: Mixed AI and Manual Operations

**Test:** Verify cart syncs between AI and manual actions

1. **Manual add:** Browse products, click "Add to Cart" on any product
2. **Verify:** Cart badge shows "1"
3. **AI add:** Open assistant, type "Add 2 more of the same item"
4. **Expected:**
   - Cart badge shows "3"
   - AI can see the manually-added item
   - Cart page shows combined items

5. **AI view:** Type "What's in my cart?"
6. **Expected:**
   - AI lists all 3 items
   - AI shows correct total

### Scenario 3: Cart Operations via AI

**Test:** AI can view, update, and manage cart

**Setup:** Add 3 different items to cart (any method)

**Test Commands:**

| User Input | Expected AI Action | Verification |
|------------|-------------------|--------------|
| "Show my cart" | Uses view_cart tool | Lists all items with prices |
| "What's my cart total?" | Uses view_cart tool | Shows correct total |
| "Remove the roses from my cart" | Uses remove_from_cart tool | Item removed, badge decrements |
| "Increase chocolate to 10" | Uses update_cart_quantity tool | Quantity updated, total recalculated |
| "Clear my cart" | Offers to use remove_from_cart on all | Cart emptied |

### Scenario 4: Cart Persistence and Session

**Test:** Cart persists across page reloads and sessions

1. Add items to cart (AI or manual)
2. Note the cart badge count (e.g., "5")
3. **Refresh page** (F5)
4. **Expected:**
   - Same cart badge count
   - Same items in cart page
   - Same sessionId in localStorage

5. **Check sessionId:**
```javascript
// Browser console
localStorage.getItem('ai_session_id')
// Should return: "session-abc123..."
```

6. **Open new tab** to same site
7. **Expected:**
   - Same cart appears (same sessionId)
   - Cart badge shows same count

8. **Close all tabs, reopen site**
9. **Expected:**
   - Cart still persists (7-day TTL)

### Scenario 5: Cart Badge Updates

**Test:** Cart badge updates in all scenarios

**Scenario A: AI adds item**
- Badge increments immediately after action card appears

**Scenario B: Manual add from product page**
- Badge increments when "Add to Cart" clicked

**Scenario C: Quantity update on cart page**
- Change quantity from 1 to 5
- Badge updates from 1 to 5

**Scenario D: Remove item from cart page**
- Click "Remove" button
- Badge decrements

**Scenario E: Clear cart**
- Click "Clear Cart"
- Badge disappears (shows 0 or hidden)

### Scenario 6: Multiple Product Configurations

**Test:** Items with different configurations are treated as separate cart items

1. **Add configured product:**
   - Navigate to customizable bike
   - Select: Frame Type = "Road", Wheel = "Carbon"
   - Add to cart
   - Badge shows "1"

2. **Add same product, different config:**
   - Select: Frame Type = "Mountain", Wheel = "Alloy"
   - Add to cart
   - Badge shows "2"

3. **Verify in cart page:**
   - [ ] Two separate line items appear
   - [ ] Each shows different configuration
   - [ ] Each can be removed independently

4. **AI test:**
   - Type: "What bikes are in my cart?"
   - **Expected:** AI lists both with different configurations

### Scenario 7: Error Handling

**Test:** Graceful handling of errors

**Test A: Backend down**
1. Stop backend: `docker compose stop`
2. Try to add item via AI
3. **Expected:**
   - Error message in console
   - User-friendly error shown
   - Cart operations fail gracefully

**Test B: Redis down**
1. Stop Redis: `docker compose stop redis`
2. Try to add item
3. **Expected:**
   - Backend returns error
   - Frontend shows error state

**Test C: Invalid session**
1. Clear localStorage
2. Refresh page (new sessionId generated)
3. Try to add item
4. **Expected:**
   - New cart created with new sessionId
   - Operations work normally

---

## Visual Inspection Checklist

### Action Card Appearance

When AI adds items, the action card should have:
- [ ] Green background (`bg-green-50`)
- [ ] Green border (`border-green-200`)
- [ ] CheckCircle icon (green)
- [ ] Heading: "Added to Cart!" or "Cart Updated"
- [ ] Item details: quantity, name, line total
- [ ] Cart total with item count
- [ ] Two buttons: "View Cart" (outline) and "Checkout Now" (solid green)
- [ ] Smooth slide-in animation

### Cart Badge Appearance

The cart badge should:
- [ ] Appear in top-right of navigation
- [ ] Be positioned at top-right of shopping cart icon
- [ ] Have teal background (`bg-teal-600`)
- [ ] Have white text
- [ ] Show item count (not quantity)
- [ ] Be circular (height and width equal)
- [ ] Only appear when itemCount > 0

### Cart Page Display

Cart page should show:
- [ ] All items from Redis backend
- [ ] Correct product names and images
- [ ] Current prices (from Redis)
- [ ] Quantity controls (+ / -)
- [ ] Remove button for each item
- [ ] Subtotal calculation
- [ ] "Continue Shopping" and "Checkout" buttons
- [ ] Empty state if cart is empty

---

## Performance Checks

### Response Times

**Acceptable response times:**
- Add to cart (manual): < 500ms
- Add to cart (AI): < 2s (includes AI processing)
- Get cart: < 200ms
- Update quantity: < 300ms
- Remove item: < 300ms

**Check Network tab:**
1. Open DevTools → Network
2. Perform cart operation
3. Find API request to `/api/ai-assistant/cart/...`
4. Check response time

### Redis Performance

```bash
# Check Redis latency
docker compose exec redis redis-cli --latency
# Should be < 1ms for most operations

# Check Redis memory usage
docker compose exec redis redis-cli INFO memory
# Look for: used_memory_human
```

---

## Debugging Tools

### Browser Console Commands

```javascript
// Get current sessionId
localStorage.getItem('ai_session_id')

// Get cart context state (React DevTools)
// 1. Install React DevTools extension
// 2. Open Components tab
// 3. Find CartProvider
// 4. Inspect state: items, itemCount, totalPrice

// Monitor cart API calls
// Network tab → Filter: "cart"
```

### Backend Logs

```bash
# View backend logs
docker compose logs -f web

# Look for:
# - "add_to_cart tool executed"
# - Cart API endpoint calls
# - Any errors or exceptions
```

### Redis Inspection

```bash
# Connect to Redis
docker compose exec redis redis-cli
> SELECT 1

# List all carts
> KEYS cart:*

# Get cart items
> SMEMBERS cart:session-abc123:items

# Get item details
> HGETALL cart:session-abc123:item:123_-9223372036854775808

# Check TTL (should be ~604800 seconds = 7 days)
> TTL cart:session-abc123:items
```

---

## Common Issues and Solutions

### Issue: Cart badge not updating after AI adds item

**Diagnosis:**
1. Check browser console for errors
2. Verify `refreshCart()` is being called in action card
3. Check Network tab for `/api/ai-assistant/cart/{sessionId}/` request

**Solution:**
- Ensure action card has `useEffect` that calls `refreshCart()`
- Verify cart context is properly imported
- Check that `itemCount` is calculated correctly in cart context

### Issue: Items disappear after page refresh

**Diagnosis:**
1. Check if sessionId persists in localStorage
2. Check Redis for cart keys

**Solution:**
- Verify `ai_session_id` in localStorage is not being cleared
- Check Redis TTL is set correctly (7 days)
- Verify cart context fetches on mount when sessionId is available

### Issue: AI adds wrong quantity

**Diagnosis:**
1. Check AI chat logs for parsed quantity
2. Check Redis item hash for stored quantity

**Solution:**
- Verify LangChain tool parameter parsing
- Check backend cart service `add_item` method
- Review AI system prompt for quantity instructions

### Issue: Cart shows different items than Redis

**Diagnosis:**
1. Check transformation in cart context `fetchCart()`
2. Verify API response format

**Solution:**
```typescript
// Cart context should transform:
const transformedItems: CartItem[] = cart.items.map((item: any) => ({
  id: item.item_id,        // Backend uses item_id
  name: item.name,
  price: item.price,
  image: item.image_url || '/placeholder.png',
  quantity: item.quantity,
  categoryId: item.category_id,
  configuration: item.configuration
}))
```

---

## Success Criteria

Phase 3 is successful when:

✅ **AI Autonomy**
- AI can add items to cart without user clicking buttons
- AI uses tools correctly (add_to_cart, view_cart, etc.)
- AI provides confirmation messages

✅ **Cart Sync**
- Cart badge updates immediately after AI adds items
- Cart page shows items from Redis backend
- Manual cart operations work correctly
- Mixed AI/manual operations sync properly

✅ **Persistence**
- Cart persists across page reloads
- Cart persists in Redis with 7-day TTL
- SessionId persists in localStorage

✅ **Visual Feedback**
- Action cards appear with correct styling
- Cart badge displays correctly
- No visual glitches or layout issues

✅ **No Regressions**
- Manual cart operations still work
- Product pages still function
- Checkout flow still accessible (even if not complete)
- No console errors during normal operations

---

**Ready to test?** Start with the Quick Start section above!

**Found issues?** Check the Debugging Tools and Common Issues sections.

**All tests passing?** Phase 3 is complete! Ready for Phase 4: Checkout Flow.
