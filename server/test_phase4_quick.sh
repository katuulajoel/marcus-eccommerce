#!/bin/bash

# Quick Phase 4 Test Script
# Tests the checkout flow via API

echo "🧪 Phase 4 Checkout Flow - Quick Test"
echo "======================================"
echo ""

BASE_URL="http://localhost:8000/api/ai-assistant"
SESSION_ID="test-$(date +%s)"

echo "📝 Session ID: $SESSION_ID"
echo ""

# Step 1: Add item to cart
echo "1️⃣  Adding item to cart..."
curl -s -X POST "$BASE_URL/cart/add/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "'$SESSION_ID'",
    "product_id": 1,
    "name": "Test Product",
    "price": 50000,
    "quantity": 2
  }' | python3 -m json.tool
echo ""

# Step 2: Initiate checkout
echo "2️⃣  Initiating checkout..."
curl -s -X POST "$BASE_URL/checkout/initiate/" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "'$SESSION_ID'"}' | python3 -m json.tool
echo ""

# Step 3: Save shipping address
echo "3️⃣  Saving shipping address..."
curl -s -X POST "$BASE_URL/checkout/address/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "'$SESSION_ID'",
    "recipient_name": "John Doe",
    "phone_number": "+256701234567",
    "address_line1": "Plot 123 Main St",
    "city": "Kampala",
    "country": "Uganda"
  }' | python3 -m json.tool
echo ""

# Step 4: Select shipping method
echo "4️⃣  Selecting standard delivery..."
curl -s -X POST "$BASE_URL/checkout/select-shipping/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "'$SESSION_ID'",
    "shipping_method": "standard"
  }' | python3 -m json.tool
echo ""

# Step 5: Create order
echo "5️⃣  Creating order..."
curl -s -X POST "$BASE_URL/checkout/create-order/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "'$SESSION_ID'",
    "customer_name": "John Doe",
    "customer_phone": "+256701234567",
    "customer_email": "john@example.com"
  }' | python3 -m json.tool
echo ""

# Step 6: Generate payment link
echo "6️⃣  Generating payment (Cash on Delivery)..."
curl -s -X POST "$BASE_URL/checkout/payment-link/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "'$SESSION_ID'",
    "payment_method": "cash_on_delivery"
  }' | python3 -m json.tool
echo ""

echo "✅ Test complete!"
echo ""
echo "To check the order in Django shell:"
echo "  docker compose exec web python manage.py shell"
echo "  >>> from apps.orders.models import Orders"
echo "  >>> Orders.objects.latest('id')"
