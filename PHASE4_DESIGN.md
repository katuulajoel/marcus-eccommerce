# Phase 4 Design: Checkout Flow

## Overview

Phase 4 enables the AI assistant to guide users through a conversational checkout experience, collecting necessary information, creating orders in PostgreSQL, and facilitating payment.

## Goals

1. **Conversational Checkout** - AI guides users through checkout naturally
2. **Address Collection** - AI asks for and validates shipping information
3. **Shipping Options** - Display available delivery methods with costs
4. **Order Creation** - Convert Redis cart → PostgreSQL order
5. **Payment Methods** - Support Stripe and Mobile Money (MTN, Airtel)
6. **Guest Checkout** - Allow checkout without account creation

## Architecture

### Data Flow

```
User: "I'm ready to checkout"
    ↓
AI: initiate_checkout tool
    ↓
Checkout Service creates checkout session
    ↓
AI: "What's your delivery address?"
    ↓
User provides address
    ↓
AI: collect_shipping_address tool
    ↓
Validate and store address
    ↓
AI: get_shipping_options tool
    ↓
Display shipping methods (pickup, standard, express)
    ↓
User selects shipping method
    ↓
AI: confirm_shipping_method tool
    ↓
AI: get_payment_methods tool
    ↓
User chooses payment method
    ↓
AI: create_order tool (Redis cart → PostgreSQL)
    ↓
AI: generate_payment_link tool (Stripe or Mobile Money)
    ↓
Return payment URL to user
```

## Database Models (Existing)

### Orders Model
- ✅ Already has all fields we need
- ✅ Supports shipping_address (FK to ShippingAddress)
- ✅ Supports shipping_cost calculation
- ✅ Supports payment_status tracking
- ✅ Supports multiple currencies

### ShippingAddress Model
- ✅ Already has all necessary fields
- ✅ Phone validation included

### Customer Model
- ✅ Supports guest customers (user=null, name/phone/email)
- ✅ Preferred currency support

### OrderProduct & OrderItem Models
- ✅ Support for configured products
- ✅ Minimum payment tracking

## New Components

### 1. Checkout Service (`checkout_service.py`)

**Purpose:** Manage checkout sessions and orchestrate checkout flow

**Methods:**

```python
class CheckoutService:
    def __init__(self):
        self.redis_client = redis.Redis(...)
        self.cart_service = get_cart_service()

    # Session Management
    def create_checkout_session(self, session_id: str) -> Dict
    def get_checkout_session(self, session_id: str) -> Dict
    def update_checkout_session(self, session_id: str, data: Dict) -> Dict

    # Address Handling
    def validate_address(self, address_data: Dict) -> Tuple[bool, str]
    def save_shipping_address(self, address_data: Dict) -> ShippingAddress

    # Shipping Options
    def get_available_shipping_methods(self, cart_total: Decimal, city: str) -> List[Dict]
    def calculate_shipping_cost(self, method: str, cart_total: Decimal) -> Decimal

    # Order Creation
    def create_order_from_cart(self, session_id: str, customer_data: Dict,
                               shipping_address_id: int, shipping_method: str) -> Orders

    # Customer Handling
    def get_or_create_customer(self, name: str, phone: str, email: str = None) -> Customer
```

**Checkout Session (Redis)**
```python
# Key: checkout:{session_id}
# TTL: 1 hour
{
    "session_id": "session-abc123",
    "status": "collecting_address|address_collected|shipping_selected|order_created",
    "customer": {
        "name": "John Doe",
        "phone": "+256701234567",
        "email": "john@example.com"
    },
    "shipping_address": {
        "recipient_name": "John Doe",
        "phone_number": "+256701234567",
        "address_line1": "Plot 123, Main Street",
        "city": "Kampala",
        "country": "Uganda"
    },
    "shipping_method": "standard",
    "shipping_cost": "15000",
    "cart_total": "240000",
    "order_id": 42,  # Set after order creation
    "created_at": "2025-10-16T10:30:00",
    "updated_at": "2025-10-16T10:35:00"
}
```

### 2. Shipping Service (`shipping_service.py`)

**Purpose:** Manage shipping methods and cost calculation

**Shipping Methods:**

```python
SHIPPING_METHODS = {
    'pickup': {
        'name': 'Store Pickup',
        'description': 'Pick up from our Kampala store',
        'base_cost': 0,
        'delivery_time': 'Same day',
        'available_cities': ['Kampala', 'Entebbe']
    },
    'standard': {
        'name': 'Standard Delivery',
        'description': 'Delivery within 2-3 business days',
        'base_cost': 15000,  # UGX
        'delivery_time': '2-3 days',
        'available_cities': ['Kampala', 'Entebbe', 'Jinja', 'Mbarara', 'Gulu']
    },
    'express': {
        'name': 'Express Delivery',
        'description': 'Next-day delivery',
        'base_cost': 30000,  # UGX
        'delivery_time': 'Next day',
        'available_cities': ['Kampala', 'Entebbe']
    }
}
```

**Cost Calculation Logic:**
- Free shipping on orders > UGX 500,000
- Standard delivery: UGX 15,000
- Express delivery: UGX 30,000
- Pickup: Free

### 3. Payment Service (`payment_service.py`)

**Purpose:** Handle payment method selection and link generation

**Payment Methods:**

```python
PAYMENT_METHODS = {
    'stripe': {
        'name': 'Credit/Debit Card',
        'description': 'Pay securely with card (Stripe)',
        'currencies': ['UGX', 'USD', 'EUR'],
        'min_amount': 1000  # UGX
    },
    'mtn_mobile_money': {
        'name': 'MTN Mobile Money',
        'description': 'Pay with MTN Mobile Money',
        'currencies': ['UGX'],
        'min_amount': 500
    },
    'airtel_money': {
        'name': 'Airtel Money',
        'description': 'Pay with Airtel Money',
        'currencies': ['UGX'],
        'min_amount': 500
    },
    'cash_on_delivery': {
        'name': 'Cash on Delivery',
        'description': 'Pay when you receive your order',
        'currencies': ['UGX'],
        'min_amount': 0
    }
}
```

**Methods:**

```python
class PaymentService:
    def get_available_payment_methods(self, order_total: Decimal, currency: str) -> List[Dict]

    # Stripe
    def create_stripe_checkout_session(self, order_id: int) -> str  # Returns URL

    # Mobile Money
    def initiate_mobile_money_payment(self, order_id: int, phone: str,
                                     provider: str) -> Dict  # Returns USSD code
```

### 4. LangChain Tools (New)

#### Tool 1: `initiate_checkout`
```python
class InitiateCheckoutTool(BaseTool):
    name = "initiate_checkout"
    description = """Start the checkout process.
    USE THIS WHEN: User says "checkout", "I'm ready to pay", "complete my order"
    """

    def _run(self, session_id: str) -> str:
        # Check cart not empty
        # Create checkout session in Redis
        # Return: "✅ Starting checkout! First, I need your delivery address..."
```

#### Tool 2: `collect_shipping_address`
```python
class CollectShippingAddressTool(BaseTool):
    name = "collect_shipping_address"
    description = """Save customer shipping address.
    USE THIS WHEN: User provides address details during checkout
    """

    def _run(self, session_id: str, recipient_name: str, phone_number: str,
             address_line1: str, city: str, country: str = "Uganda",
             address_line2: str = None) -> str:
        # Validate address
        # Save to checkout session
        # Return shipping options
```

#### Tool 3: `get_shipping_options`
```python
class GetShippingOptionsTool(BaseTool):
    name = "get_shipping_options"
    description = """Get available shipping methods for the order.
    USE THIS WHEN: User asks about delivery options or after address is collected
    """

    def _run(self, session_id: str) -> str:
        # Get checkout session
        # Calculate shipping costs
        # Return formatted list of options
```

#### Tool 4: `select_shipping_method`
```python
class SelectShippingMethodTool(BaseTool):
    name = "select_shipping_method"
    description = """Set the shipping method for the order.
    USE THIS WHEN: User chooses a delivery method
    """

    def _run(self, session_id: str, shipping_method: str) -> str:
        # Validate method
        # Update checkout session
        # Return payment options
```

#### Tool 5: `create_order`
```python
class CreateOrderTool(BaseTool):
    name = "create_order"
    description = """Create the order in the database from the cart.
    USE THIS WHEN: User confirms they want to proceed with payment
    """

    def _run(self, session_id: str, customer_name: str, customer_phone: str,
             customer_email: str = None) -> str:
        # Get cart from Redis
        # Get checkout session
        # Create Customer (or get existing)
        # Create ShippingAddress
        # Create Order, OrderProduct, OrderItem
        # Return order confirmation
```

#### Tool 6: `generate_payment_link`
```python
class GeneratePaymentLinkTool(BaseTool):
    name = "generate_payment_link"
    description = """Generate payment link or USSD code for the order.
    USE THIS WHEN: User selects payment method
    """

    def _run(self, session_id: str, payment_method: str) -> str:
        # Get order from checkout session
        # Generate payment link (Stripe) or USSD code (Mobile Money)
        # Return payment instructions
```

### 5. API Endpoints (New)

```python
# In apps/ai_assistant/urls.py
path('checkout/initiate/', views.initiate_checkout, name='initiate_checkout'),
path('checkout/<str:session_id>/', views.get_checkout_session, name='get_checkout_session'),
path('checkout/address/', views.save_shipping_address, name='save_shipping_address'),
path('checkout/shipping-options/', views.get_shipping_options, name='get_shipping_options'),
path('checkout/select-shipping/', views.select_shipping_method, name='select_shipping_method'),
path('checkout/create-order/', views.create_order_from_cart, name='create_order_from_cart'),
path('checkout/payment-link/', views.generate_payment_link, name='generate_payment_link'),
```

### 6. Updated AI System Prompt

```python
# Add to agent_service.py system prompt

CHECKOUT FLOW - GUIDE USER STEP BY STEP:

**WHEN USER SAYS "checkout", "ready to pay", "complete order":**
1. Use `initiate_checkout` tool
2. Ask: "What's your delivery address?"

**WHEN USER PROVIDES ADDRESS:**
1. Parse address details (name, phone, street, city)
2. Use `collect_shipping_address` tool
3. Use `get_shipping_options` tool
4. Show shipping options with prices
5. Ask: "Which delivery method do you prefer?"

**WHEN USER SELECTS SHIPPING:**
1. Use `select_shipping_method` tool
2. Show order summary with shipping cost
3. Confirm customer details (name, phone, email)
4. Ask: "How would you like to pay?"

**WHEN USER SELECTS PAYMENT:**
1. Use `create_order` tool (creates order in DB)
2. Use `generate_payment_link` tool
3. Provide payment link or USSD code
4. Give order confirmation: "Order #42 created! Total: UGX 255,000"

**PAYMENT METHODS:**
- Card Payment (Stripe) - share payment link
- MTN Mobile Money - share USSD code: *165*3#
- Airtel Money - share USSD code: *185*9#
- Cash on Delivery - confirm order, no payment link needed

**ADDRESS FORMAT:**
Ask for: Name, Phone, Street Address, City
Example: "John Doe, +256701234567, Plot 123 Main St, Kampala"
```

### 7. Frontend Action Cards (New Types)

**Checkout Initiated Card:**
```typescript
{
  type: 'checkout_initiated',
  message: 'Starting checkout...',
  cart_summary: {...}
}
```

**Address Collected Card:**
```typescript
{
  type: 'address_collected',
  address: {
    recipient_name: 'John Doe',
    address_line1: 'Plot 123 Main St',
    city: 'Kampala'
  }
}
```

**Shipping Options Card:**
```typescript
{
  type: 'shipping_options',
  options: [
    {
      method: 'pickup',
      name: 'Store Pickup',
      cost: 0,
      delivery_time: 'Same day'
    },
    {
      method: 'standard',
      name: 'Standard Delivery',
      cost: 15000,
      delivery_time: '2-3 days'
    }
  ]
}
```

**Order Created Card:**
```typescript
{
  type: 'order_created',
  order_id: 42,
  order_total: 255000,
  shipping_method: 'Standard Delivery',
  delivery_address: 'Plot 123 Main St, Kampala'
}
```

**Payment Link Card:**
```typescript
{
  type: 'payment_link',
  payment_method: 'stripe',
  payment_url: 'https://checkout.stripe.com/...',
  order_id: 42,
  amount: 255000
}
```

**Mobile Money Card:**
```typescript
{
  type: 'mobile_money_payment',
  provider: 'MTN Mobile Money',
  ussd_code: '*165*3#',
  amount: 255000,
  phone_number: '+256701234567',
  instructions: 'Dial *165*3# and follow prompts...'
}
```

## Implementation Order

### Step 1: Backend Services (Core Logic)
1. Create `checkout_service.py` - Checkout session management
2. Create `shipping_service.py` - Shipping methods and costs
3. Create `payment_service.py` (basic) - Payment method listing

### Step 2: LangChain Tools
1. Add 6 new tools to `langchain_tools.py`
2. Update AI system prompt in `agent_service.py`

### Step 3: API Endpoints
1. Add 7 checkout endpoints to `views.py`
2. Add routes to `urls.py`

### Step 4: Payment Integration (Phase 4a - Stripe)
1. Add Stripe SDK to requirements.txt
2. Implement `create_stripe_checkout_session`
3. Add Stripe webhook handler for payment confirmation

### Step 5: Payment Integration (Phase 4b - Mobile Money)
1. Research Mobile Money API options (Flutterwave, Paystack)
2. Implement basic USSD code generation
3. Add payment confirmation webhook

### Step 6: Frontend Updates
1. Add new action card types to `ai-action-card.tsx`
2. Add checkout context (optional, for tracking checkout state)
3. Update order confirmation page

### Step 7: Testing
1. Test conversational checkout flow
2. Test order creation from cart
3. Test Stripe payment links
4. Test Mobile Money USSD codes

## Environment Variables Needed

```bash
# .env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Mobile Money (future)
FLUTTERWAVE_PUBLIC_KEY=...
FLUTTERWAVE_SECRET_KEY=...
```

## Testing Scenarios

### Scenario 1: Full Checkout Flow
```
User: "I want 2 balloon bouquets"
AI: [Adds to cart]
User: "Checkout"
AI: "What's your delivery address?"
User: "John Doe, +256701234567, Plot 123 Main St, Kampala"
AI: [Shows shipping options]
User: "Standard delivery"
AI: "How would you like to pay?"
User: "Card payment"
AI: [Creates order, generates Stripe link]
```

### Scenario 2: Guest Checkout
- No login required
- AI collects name, phone, email during checkout
- Creates guest Customer record

### Scenario 3: Address Validation
- Invalid phone format → AI asks for correction
- Missing city → AI prompts for missing info

### Scenario 4: Shipping Cost Calculation
- Free shipping on orders > UGX 500,000
- Standard delivery cost added to total

### Scenario 5: Multiple Payment Methods
- Card payment → Stripe link
- MTN Mobile Money → USSD code
- Cash on delivery → Order created, no payment link

## Success Criteria

Phase 4 is successful when:

✅ AI can guide users through complete checkout
✅ Address collection and validation works
✅ Shipping options display correctly
✅ Orders created in PostgreSQL from Redis cart
✅ Stripe payment links generated
✅ Mobile Money USSD codes provided
✅ Order confirmation with order number
✅ Cart cleared after order creation

## Out of Scope (Phase 5)

- WhatsApp checkout flow
- Order tracking and status updates
- Email/SMS notifications
- Payment confirmation webhooks (basic version only)

---

**Ready to implement!**
