#!/bin/bash
# Cart API Endpoint Testing Script
# Tests all cart endpoints via curl

BASE_URL="http://localhost:8000/api/ai-assistant"
SESSION_ID="test-api-session-$(date +%s)"

echo "======================================"
echo "Cart API Endpoint Tests"
echo "======================================"
echo "Session ID: $SESSION_ID"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Add item to cart
echo -e "${YELLOW}Test 1: Add item to cart${NC}"
echo "POST $BASE_URL/cart/add/"
response=$(curl -s -X POST "$BASE_URL/cart/add/" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"product_id\": 1,
    \"name\": \"Hot Air Balloon Bouquet\",
    \"price\": 120000,
    \"quantity\": 2,
    \"image_url\": \"https://example.com/balloon.jpg\",
    \"category_id\": 1
  }")

if echo "$response" | grep -q "subtotal"; then
  echo -e "${GREEN}✅ PASS${NC}: Item added successfully"
  echo "$response" | python3 -m json.tool
else
  echo -e "${RED}❌ FAIL${NC}: Failed to add item"
  echo "$response"
fi
echo ""

# Test 2: Get cart
echo -e "${YELLOW}Test 2: Get cart${NC}"
echo "GET $BASE_URL/cart/$SESSION_ID/"
response=$(curl -s "$BASE_URL/cart/$SESSION_ID/")

if echo "$response" | grep -q "subtotal"; then
  echo -e "${GREEN}✅ PASS${NC}: Cart retrieved successfully"
  echo "$response" | python3 -m json.tool
else
  echo -e "${RED}❌ FAIL${NC}: Failed to get cart"
  echo "$response"
fi
echo ""

# Test 3: Add second item
echo -e "${YELLOW}Test 3: Add second item${NC}"
echo "POST $BASE_URL/cart/add/"
response=$(curl -s -X POST "$BASE_URL/cart/add/" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"product_id\": 2,
    \"name\": \"Explosion Box - Boyfriend Kit\",
    \"price\": 135000,
    \"quantity\": 1,
    \"category_id\": 2
  }")

if echo "$response" | grep -q "subtotal"; then
  echo -e "${GREEN}✅ PASS${NC}: Second item added"
  item_count=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['item_count'])")
  echo "Total items in cart: $item_count"
else
  echo -e "${RED}❌ FAIL${NC}: Failed to add second item"
  echo "$response"
fi
echo ""

# Test 4: Update quantity
echo -e "${YELLOW}Test 4: Update quantity${NC}"
# Get first item ID
cart_response=$(curl -s "$BASE_URL/cart/$SESSION_ID/")
item_id=$(echo "$cart_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['items'][0]['item_id'])")

echo "Updating item $item_id to quantity 5"
response=$(curl -s -X POST "$BASE_URL/cart/update-quantity/" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"item_id\": \"$item_id\",
    \"quantity\": 5
  }")

if echo "$response" | grep -q "subtotal"; then
  echo -e "${GREEN}✅ PASS${NC}: Quantity updated"
  subtotal=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['subtotal'])")
  echo "New subtotal: UGX $subtotal"
else
  echo -e "${RED}❌ FAIL${NC}: Failed to update quantity"
  echo "$response"
fi
echo ""

# Test 5: Remove item
echo -e "${YELLOW}Test 5: Remove item${NC}"
echo "Removing item $item_id"
response=$(curl -s -X POST "$BASE_URL/cart/remove/" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"item_id\": \"$item_id\"
  }")

if echo "$response" | grep -q "subtotal"; then
  echo -e "${GREEN}✅ PASS${NC}: Item removed"
  item_count=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['item_count'])")
  echo "Remaining items: $item_count"
else
  echo -e "${RED}❌ FAIL${NC}: Failed to remove item"
  echo "$response"
fi
echo ""

# Test 6: Clear cart
echo -e "${YELLOW}Test 6: Clear cart${NC}"
response=$(curl -s -X POST "$BASE_URL/cart/clear/" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\"
  }")

if echo "$response" | grep -q "cleared successfully"; then
  echo -e "${GREEN}✅ PASS${NC}: Cart cleared"
  echo "$response"
else
  echo -e "${RED}❌ FAIL${NC}: Failed to clear cart"
  echo "$response"
fi
echo ""

# Test 7: Verify cart is empty
echo -e "${YELLOW}Test 7: Verify cart is empty${NC}"
response=$(curl -s "$BASE_URL/cart/$SESSION_ID/")

if echo "$response" | grep -q '"item_count": 0'; then
  echo -e "${GREEN}✅ PASS${NC}: Cart is empty"
  echo "$response" | python3 -m json.tool
else
  echo -e "${RED}❌ FAIL${NC}: Cart is not empty"
  echo "$response"
fi
echo ""

echo "======================================"
echo "API Tests Complete!"
echo "======================================"
