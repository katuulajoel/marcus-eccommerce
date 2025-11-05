"""
LangChain Tools for Marcus E-commerce
These tools allow the LangChain agent to interact with the e-commerce platform.
Tools are dynamically powered by Django models - no hardcoding!
"""

from typing import Optional, List, Dict
from decimal import Decimal
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from .index_service import get_index_service
from .context_builder import context_builder
from .cart_service import get_cart_service
from .checkout_service import get_checkout_service
from .shipping_service import get_shipping_service
from .payment_service import get_payment_service


# Tool Input Schemas
class SearchProductsInput(BaseModel):
    """Input for searching products"""
    query: str = Field(description="Natural language search query for products")
    category_id: Optional[int] = Field(default=None, description="Optional category ID to filter results")


class SearchCategoriesInput(BaseModel):
    """Input for searching categories"""
    query: str = Field(description="Natural language search query for categories")


class ValidateConfigurationInput(BaseModel):
    """Input for validating product configuration"""
    category_id: int = Field(description="Category ID for the product being configured")
    configuration: Dict[str, str] = Field(description="Dictionary mapping part names to option IDs")


class CalculatePriceInput(BaseModel):
    """Input for calculating product price"""
    category_id: int = Field(description="Category ID")
    configuration: Dict[str, str] = Field(description="Dictionary mapping part names to option IDs")


class GetPartOptionsInput(BaseModel):
    """Input for getting part options"""
    part_name: str = Field(description="Name of the part (e.g., 'Frame', 'Wheels')")
    category_id: int = Field(description="Category ID")


class GetAvailableCategoriesInput(BaseModel):
    """Input for getting available categories"""
    pass  # No input needed


# Cart Action Tool Input Schemas
class AddToCartInput(BaseModel):
    """Input for adding items to cart"""
    session_id: str = Field(description="User's session ID (from AI chat session)")
    product_id: int = Field(description="Product ID from search results")
    product_name: str = Field(description="Name of the product to add")
    price: float = Field(description="Price per unit in UGX")
    quantity: int = Field(default=1, description="Quantity to add (default: 1)")
    configuration: Optional[Dict] = Field(default=None, description="Product configuration (for customizable products)")
    image_url: Optional[str] = Field(default=None, description="Product image URL")
    category_id: Optional[int] = Field(default=None, description="Category ID")


class ViewCartInput(BaseModel):
    """Input for viewing cart"""
    session_id: str = Field(description="User's session ID")


class RemoveFromCartInput(BaseModel):
    """Input for removing items from cart"""
    session_id: str = Field(description="User's session ID")
    item_id: str = Field(description="Item ID to remove (from cart display)")


class UpdateCartQuantityInput(BaseModel):
    """Input for updating item quantity"""
    session_id: str = Field(description="User's session ID")
    item_id: str = Field(description="Item ID to update")
    quantity: int = Field(description="New quantity (0 to remove)")


# Checkout Action Tool Input Schemas
class InitiateCheckoutInput(BaseModel):
    """Input for initiating checkout"""
    session_id: str = Field(description="User's session ID")


class CollectShippingAddressInput(BaseModel):
    """Input for collecting shipping address"""
    session_id: str = Field(description="User's session ID")
    recipient_name: str = Field(description="Recipient's full name")
    phone_number: str = Field(description="Phone number with country code (e.g., +256701234567)")
    address_line1: str = Field(description="Street address")
    city: str = Field(description="City name")
    country: str = Field(default="Uganda", description="Country name")
    address_line2: Optional[str] = Field(default=None, description="Additional address line (optional)")


class GetShippingOptionsInput(BaseModel):
    """Input for getting shipping options"""
    session_id: str = Field(description="User's session ID")


class SelectShippingMethodInput(BaseModel):
    """Input for selecting shipping method"""
    session_id: str = Field(description="User's session ID")
    shipping_method: str = Field(description="Shipping method code (pickup, standard, express)")


class CreateOrderInput(BaseModel):
    """Input for creating order"""
    session_id: str = Field(description="User's session ID")
    customer_name: str = Field(description="Customer's full name")
    customer_phone: str = Field(description="Customer's phone number")
    customer_email: Optional[str] = Field(default=None, description="Customer's email (optional)")


class GeneratePaymentLinkInput(BaseModel):
    """Input for generating payment link"""
    session_id: str = Field(description="User's session ID")
    payment_method: str = Field(description="Payment method code (stripe, mtn_mobile_money, airtel_money, cash_on_delivery)")


# LangChain Tools
class SearchProductsTool(BaseTool):
    """
    Search for products using semantic search.
    Powered by LlamaIndex - automatically searches all products in database.
    """
    name: str = "search_products"
    description: str = """
    Search for products based on natural language query.
    Use this when user asks about specific products, wants recommendations,
    or is looking for products with certain features.

    Example queries:
    - "I need a mountain bike"
    - "Show me beginner-friendly bikes"
    - "What's your cheapest bike?"
    - "I want something for trail riding"

    Returns list of matching products with prices and descriptions.
    """
    args_schema: type[BaseModel] = SearchProductsInput

    def _run(self, query: str, category_id: Optional[int] = None) -> str:
        """Execute the search"""
        from apps.preconfigured_products.models import PreConfiguredProduct

        index_service = get_index_service()
        products = index_service.search_products(query, category_id)

        if not products:
            return f"No products found matching '{query}'. Try a different search."

        # Format results with additional product details
        result = f"Found {len(products)} matching products:\n\n"
        for i, product in enumerate(products[:5], 1):  # Top 5
            product_id = product.get('id')

            # Fetch full product details including image
            try:
                db_product = PreConfiguredProduct.objects.get(id=product_id)
                image_url = db_product.image.url if db_product.image else None
            except PreConfiguredProduct.DoesNotExist:
                image_url = None

            result += f"{i}. {product['name']}\n"
            result += f"   Product ID: {product_id}\n"
            result += f"   Category: {product['category']}\n"
            result += f"   Price: UGX {product['base_price']}\n"
            if image_url:
                result += f"   Image URL: {image_url}\n"
            result += f"   Relevance: {product['relevance_score']:.2f}\n\n"

        result += "\n**IMPORTANT**: When adding to cart, use the Product ID and Image URL from above!"
        return result

    def _arun(self, query: str, category_id: Optional[int] = None):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


class SearchCategoriesTool(BaseTool):
    """
    Search for product categories using semantic search.
    Dynamically discovers all categories from database.
    """
    name: str = "search_categories"
    description: str = """
    Search for product categories based on natural language query.
    Use this when user asks what types of products are available,
    or wants to browse categories.

    Example queries:
    - "What types of products do you sell?"
    - "Show me all categories"
    - "Do you have bikes?"

    Returns list of matching categories.
    """
    args_schema: type[BaseModel] = SearchCategoriesInput

    def _run(self, query: str) -> str:
        """Execute the search"""
        index_service = get_index_service()
        categories = index_service.search_categories(query)

        if not categories:
            # Fallback to context builder
            all_categories = context_builder.get_categories()
            result = "Available categories:\n\n"
            for cat in all_categories:
                result += f"- {cat['name']}: {cat['description']}\n"
            return result

        result = f"Found {len(categories)} matching categories:\n\n"
        for cat in categories:
            result += f"- {cat['name']} ({cat['parts_count']} customizable parts)\n"

        return result

    def _arun(self, query: str):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


class ValidateConfigurationTool(BaseTool):
    """
    Validate a product configuration for compatibility issues.
    Checks incompatibility rules from database.
    """
    name: str = "validate_configuration"
    description: str = """
    Validate if a product configuration is compatible.
    Use this when user has selected parts and you need to check
    if they work together, or when suggesting configurations.

    Checks:
    - Incompatibility between selected parts
    - Price adjustments (discounts/premiums)
    - Configuration completeness

    Returns validation results with issues and suggestions.
    """
    args_schema: type[BaseModel] = ValidateConfigurationInput

    def _run(self, category_id: int, configuration: Dict[str, str]) -> str:
        """Execute validation"""
        validation = context_builder.validate_configuration(category_id, configuration)

        result = ""
        if validation['is_valid']:
            result = "✓ Configuration is valid!\n\n"
        else:
            result = "✗ Configuration has issues:\n\n"
            for issue in validation['issues']:
                result += f"- {issue['message']}\n"
            result += "\n"

        if validation['suggestions']:
            result += "Suggestions:\n"
            for suggestion in validation['suggestions']:
                if isinstance(suggestion, dict):
                    result += f"- {suggestion.get('message', suggestion)}\n"
                else:
                    result += f"- {suggestion}\n"

        return result

    def _arun(self, category_id: int, configuration: Dict[str, str]):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


class GetPartOptionsTool(BaseTool):
    """
    Get available options for a specific part.
    Dynamically queries database for current inventory.
    """
    name: str = "get_part_options"
    description: str = """
    Get available options for a specific part type.
    Use this when user asks about customization options,
    wants to see what's available for a part, or needs pricing info.

    Example queries:
    - "What frame options are available?"
    - "Show me wheel choices"
    - "How much do different handlebars cost?"

    Returns list of options with prices and stock status.
    """
    args_schema: type[BaseModel] = GetPartOptionsInput

    def _run(self, part_name: str, category_id: int) -> str:
        """Get part options"""
        options = context_builder.get_part_options(part_name, category_id)

        if not options:
            return f"No options found for {part_name}. This part may not exist in the selected category."

        result = f"Available {part_name} options:\n\n"
        for option in options:
            stock = "✓ In Stock" if option.get('in_stock', True) else "✗ Out of Stock"
            result += f"- {option['name']}: ${option['price']} ({stock})\n"
            if option.get('description'):
                result += f"  {option['description']}\n"

        return result

    def _arun(self, part_name: str, category_id: int):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


class GetAvailableCategoriesTool(BaseTool):
    """
    Get all available product categories.
    Simple tool to list all categories without search.
    """
    name: str = "get_available_categories"
    description: str = """
    Get a complete list of all product categories available in the store.
    Use this for a straightforward category listing.

    Returns all categories with descriptions.
    """
    args_schema: type[BaseModel] = GetAvailableCategoriesInput

    def _run(self) -> str:
        """Get all categories"""
        categories = context_builder.get_categories()

        result = "Available product categories:\n\n"
        for cat in categories:
            result += f"- {cat['name']} (ID: {cat['id']})\n"
            if cat.get('description'):
                result += f"  {cat['description']}\n"
            result += "\n"

        return result

    def _arun(self):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


class GetPriceRangeTool(BaseTool):
    """
    Get price ranges for products in a category.
    Uses dynamically calculated min/max from database.
    """
    name: str = "get_price_range"
    description: str = """
    Get price range information for a category.
    Use this when user asks about budget, pricing, or cost ranges.

    Example queries:
    - "How much do bikes cost?"
    - "What's your price range?"
    - "Do you have anything under $500?"

    Returns cheapest and most expensive configurations.
    """
    args_schema: type[BaseModel] = SearchCategoriesInput  # Reuse this schema

    def _run(self, query: str) -> str:
        """Get price ranges"""
        # Get cheapest and most expensive configs
        cheapest = context_builder.calculate_cheapest_configurations()
        expensive = context_builder.calculate_most_expensive_configurations()

        # Try to match query to category
        index_service = get_index_service()
        categories = index_service.search_categories(query)

        result = "Price Ranges:\n\n"

        if categories:
            # Show specific category
            cat_name = categories[0]['name']
            if cat_name in cheapest:
                result += f"{cat_name}:\n"
                result += f"  Cheapest: ${cheapest[cat_name]['total_cost']:.2f}\n"
                result += f"  Most Expensive: ${expensive[cat_name]['total_cost']:.2f}\n"
        else:
            # Show all categories
            for cat_name in cheapest.keys():
                result += f"{cat_name}:\n"
                result += f"  Cheapest: ${cheapest[cat_name]['total_cost']:.2f}\n"
                result += f"  Most Expensive: ${expensive[cat_name]['total_cost']:.2f}\n\n"

        return result

    def _arun(self, query: str):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


# ============================================================================
# CART ACTION TOOLS - Enable AI to autonomously manage shopping cart
# ============================================================================

class AddToCartTool(BaseTool):
    """
    Add items to user's shopping cart.
    **IMPORTANT**: This is an ACTION tool - AI can autonomously add items!
    """
    name: str = "add_to_cart"
    description: str = """
    Add a product to the user's shopping cart in Redis.

    **USE THIS WHEN:**
    - User expresses clear intent to buy: "I want", "Add to cart", "Order", "Buy"
    - User confirms after seeing product recommendations

    **ASK FIRST if intent is unclear:**
    - "Should I add this to your cart?"
    - "Would you like me to add [product] for you?"

    **ALWAYS respond with:**
    - What was added: "✅ Added 2x Balloon Bouquet"
    - Price breakdown: "(UGX 120,000 each = UGX 240,000)"
    - Cart total: "Cart total: UGX 375,000"
    - Call to action: "Ready to checkout?"

    Returns: Cart summary with total
    """
    args_schema: type[BaseModel] = AddToCartInput

    def _run(
        self,
        session_id: str,
        product_id: int,
        product_name: str,
        price: float,
        quantity: int = 1,
        configuration: Optional[Dict] = None,
        image_url: Optional[str] = None,
        category_id: Optional[int] = None
    ) -> str:
        """Add item to cart and return confirmation"""
        from apps.preconfigured_products.models import PreConfiguredProduct, PreConfiguredProductParts

        cart_service = get_cart_service()

        # Fetch product details including image and parts configuration
        config_details = {}
        try:
            db_product = PreConfiguredProduct.objects.get(id=product_id)

            # Get image if not provided
            if not image_url:
                image_url = db_product.image.url if db_product.image else None

            # Get configured parts for display
            config_parts = PreConfiguredProductParts.objects.filter(
                preconfigured_product=db_product
            ).select_related('part_option', 'part_option__part')

            for config_part in config_parts:
                part_option = config_part.part_option
                part_name = part_option.part.name
                config_details[part_name] = {
                    'name': part_option.name,
                    'price': float(part_option.default_price)
                }
        except PreConfiguredProduct.DoesNotExist:
            pass

        # Add to cart with config details
        cart_service.add_item(
            session_id=session_id,
            product_id=product_id,
            name=product_name,
            price=Decimal(str(price)),
            quantity=quantity,
            configuration=configuration,
            config_details=config_details,
            image_url=image_url,
            category_id=category_id
        )

        # Get updated cart
        cart = cart_service.get_cart(session_id)

        # Format response
        unit_price = f"UGX {price:,.0f}"
        line_total = f"UGX {price * quantity:,.0f}"
        cart_total = f"UGX {cart['subtotal']:,.0f}"

        result = f"✅ Added {quantity}x {product_name} to cart!\n\n"

        if quantity > 1:
            result += f"Price: {unit_price} each = {line_total}\n"
        else:
            result += f"Price: {unit_price}\n"

        result += f"\nCart Summary:\n"
        result += f"- Total items: {cart['item_count']}\n"
        result += f"- Subtotal: {cart_total}\n\n"
        result += "Ready to checkout?"

        return result

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")


class ViewCartTool(BaseTool):
    """View current cart contents"""
    name: str = "view_cart"
    description: str = """
    Get the current contents of user's shopping cart from Redis.

    **USE THIS WHEN:**
    - User asks "what's in my cart?"
    - User asks "show my cart" or "cart summary"
    - Before checkout to review items

    Returns: Detailed cart summary with all items and total
    """
    args_schema: type[BaseModel] = ViewCartInput

    def _run(self, session_id: str) -> str:
        """Retrieve and format cart contents"""
        cart_service = get_cart_service()
        cart = cart_service.get_cart(session_id)

        if cart['item_count'] == 0:
            return "🛒 Your cart is empty.\n\nCan I help you find something?"

        result = f"🛒 Your Shopping Cart ({cart['item_count']} items):\n\n"

        for item in cart['items']:
            result += f"• {item['quantity']}x {item['name']}\n"
            result += f"  UGX {item['price']:,.0f} each"

            if item['quantity'] > 1:
                result += f" = UGX {item['line_total']:,.0f}"

            result += "\n"

            # Show configuration if exists
            if item.get('configuration') and item['configuration']:
                result += f"  Configuration: {item['configuration']}\n"

            result += "\n"

        result += f"Subtotal: UGX {cart['subtotal']:,.0f}\n\n"
        result += "Would you like to proceed to checkout?"

        return result

    def _arun(self, session_id: str):
        raise NotImplementedError("Async not supported")


class RemoveFromCartTool(BaseTool):
    """Remove items from cart"""
    name: str = "remove_from_cart"
    description: str = """
    Remove a specific item from the user's cart.

    **USE THIS WHEN:**
    - User says "remove [item]" or "delete [item]"
    - User changes mind about a product
    - User wants to clear specific items

    Returns: Updated cart summary
    """
    args_schema: type[BaseModel] = RemoveFromCartInput

    def _run(self, session_id: str, item_id: str) -> str:
        """Remove item and return updated cart"""
        cart_service = get_cart_service()

        # Get item details before removing (for confirmation message)
        item = cart_service.get_item(session_id, item_id)

        if not item:
            return "Item not found in cart. Please check the item ID."

        # Remove item
        cart_service.remove_item(session_id, item_id)

        # Get updated cart
        cart = cart_service.get_cart(session_id)

        result = f"✅ Removed {item['name']} from cart.\n\n"

        if cart['item_count'] > 0:
            result += f"Updated Cart:\n"
            result += f"- Total items: {cart['item_count']}\n"
            result += f"- Subtotal: UGX {cart['subtotal']:,.0f}"
        else:
            result += "Your cart is now empty."

        return result

    def _arun(self, session_id: str, item_id: str):
        raise NotImplementedError("Async not supported")


class UpdateCartQuantityTool(BaseTool):
    """Update item quantity in cart"""
    name: str = "update_cart_quantity"
    description: str = """
    Update the quantity of an item in the cart.

    **USE THIS WHEN:**
    - User wants to change quantity: "change to 3", "I want 5 instead"
    - User wants more or less of an item

    **NOTE:** Setting quantity to 0 removes the item

    Returns: Updated cart summary
    """
    args_schema: type[BaseModel] = UpdateCartQuantityInput

    def _run(self, session_id: str, item_id: str, quantity: int) -> str:
        """Update quantity and return updated cart"""
        cart_service = get_cart_service()

        # Get item for name
        item = cart_service.get_item(session_id, item_id)
        if not item:
            return "Item not found in cart."

        # Update quantity
        updated_item = cart_service.update_quantity(session_id, item_id, quantity)

        # Get updated cart
        cart = cart_service.get_cart(session_id)

        if quantity == 0 or not updated_item:
            return f"✅ Removed {item['name']} from cart.\n\nCart total: UGX {cart['subtotal']:,.0f}"

        result = f"✅ Updated {item['name']} to {quantity}x\n\n"
        result += f"Line total: UGX {updated_item['line_total']:,.0f}\n"
        result += f"Cart total: UGX {cart['subtotal']:,.0f}"

        return result

    def _arun(self, session_id: str, item_id: str, quantity: int):
        raise NotImplementedError("Async not supported")


# ========== Checkout Tools (Phase 4) ==========

class InitiateCheckoutTool(BaseTool):
    """Start the checkout process"""
    name: str = "initiate_checkout"
    description: str = """
    Start the checkout process for the user's cart.

    **USE THIS WHEN:**
    - User says "checkout", "I'm ready to pay", "complete my order"
    - User wants to finalize their purchase
    - User asks "how do I pay?"

    **AFTER USING THIS TOOL:**
    - Ask for delivery address
    - Guide user through address collection

    Returns: Checkout session created, ready for address collection
    """
    args_schema: type[BaseModel] = InitiateCheckoutInput

    def _run(self, session_id: str) -> str:
        """Initiate checkout and return next steps"""
        checkout_service = get_checkout_service()
        cart_service = get_cart_service()

        # Check if cart has items
        cart = cart_service.get_cart(session_id)
        if not cart.get('items') or cart.get('item_count', 0) == 0:
            return "❌ Your cart is empty! Please add some items before checking out."

        try:
            # Create checkout session
            checkout = checkout_service.create_checkout_session(session_id)

            cart_total = float(checkout['cart_total'])
            item_count = checkout['item_count']

            result = f"✅ **Starting checkout!**\n\n"
            result += f"Cart: {item_count} item(s) - UGX {cart_total:,.0f}\n\n"
            result += f"📍 **Next step:** I need your delivery address.\n\n"
            result += f"Please provide:\n"
            result += f"- Your full name\n"
            result += f"- Phone number (with country code, e.g., +256...)\n"
            result += f"- Street address\n"
            result += f"- City\n\n"
            result += f"Example: 'John Doe, +256701234567, Plot 123 Main St, Kampala'"

            return result

        except ValueError as e:
            return f"❌ Error: {str(e)}"
        except Exception as e:
            return f"❌ Failed to start checkout: {str(e)}"

    def _arun(self, session_id: str):
        raise NotImplementedError("Async not supported")


class CollectShippingAddressTool(BaseTool):
    """Collect and validate shipping address"""
    name: str = "collect_shipping_address"
    description: str = """
    Save customer's shipping address and show shipping options.

    **USE THIS WHEN:**
    - User provides their delivery address
    - User gives name, phone, street address, and city

    **WHAT TO EXTRACT FROM USER MESSAGE:**
    - recipient_name: Full name
    - phone_number: Phone with country code (+256...)
    - address_line1: Street address
    - city: City name
    - country: Default to "Uganda" if not specified

    **AFTER USING THIS TOOL:**
    - Show available shipping options
    - Ask user to select shipping method

    Returns: Address saved, shipping options displayed
    """
    args_schema: type[BaseModel] = CollectShippingAddressInput

    def _run(self, session_id: str, recipient_name: str, phone_number: str,
             address_line1: str, city: str, country: str = "Uganda",
             address_line2: Optional[str] = None) -> str:
        """Collect address and return shipping options"""
        checkout_service = get_checkout_service()
        shipping_service = get_shipping_service()

        # Validate address
        address_data = {
            'recipient_name': recipient_name,
            'phone_number': phone_number,
            'address_line1': address_line1,
            'address_line2': address_line2 or '',
            'city': city,
            'country': country
        }

        is_valid, error = checkout_service.validate_address(address_data)
        if not is_valid:
            return f"❌ Address validation failed: {error}\n\nPlease provide correct information."

        try:
            # Update checkout session with address
            checkout_service.update_checkout_session(session_id, {
                'shipping_address': address_data,
                'status': 'address_collected'
            })

            # Get shipping options
            checkout = checkout_service.get_checkout_session(session_id)
            cart_total = Decimal(checkout['cart_total'])

            shipping_methods = shipping_service.get_available_shipping_methods(
                cart_total=cart_total,
                city=city
            )

            # Format response
            result = f"✅ **Address confirmed!**\n\n"
            result += f"📍 Delivering to:\n"
            result += f"{recipient_name}\n{address_line1}\n{city}, {country}\n"
            result += f"📱 {phone_number}\n\n"

            # Show shipping options
            result += shipping_service.format_shipping_options_message(
                shipping_methods, cart_total
            )

            result += f"\n\nWhich delivery method would you prefer?"

            return result

        except Exception as e:
            return f"❌ Failed to save address: {str(e)}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")


class GetShippingOptionsTool(BaseTool):
    """Get available shipping options"""
    name: str = "get_shipping_options"
    description: str = """
    Get available shipping methods for the order.

    **USE THIS WHEN:**
    - User asks "what delivery options are available?"
    - User wants to see shipping costs
    - Address is already collected

    Returns: List of shipping methods with costs and delivery times
    """
    args_schema: type[BaseModel] = GetShippingOptionsInput

    def _run(self, session_id: str) -> str:
        """Get and display shipping options"""
        checkout_service = get_checkout_service()
        shipping_service = get_shipping_service()

        checkout = checkout_service.get_checkout_session(session_id)
        if not checkout:
            return "❌ No checkout session found. Please start checkout first."

        address = checkout.get('shipping_address', {})
        if not address.get('city'):
            return "❌ Please provide your delivery address first."

        cart_total = Decimal(checkout['cart_total'])
        city = address['city']

        shipping_methods = shipping_service.get_available_shipping_methods(
            cart_total=cart_total,
            city=city
        )

        result = shipping_service.format_shipping_options_message(
            shipping_methods, cart_total
        )
        result += "\n\nWhich delivery method would you prefer?"

        return result

    def _arun(self, session_id: str):
        raise NotImplementedError("Async not supported")


class SelectShippingMethodTool(BaseTool):
    """Select shipping method and IMMEDIATELY CREATE ORDER"""
    name: str = "select_shipping_method"
    description: str = """
    Set the shipping method and CREATE THE ORDER immediately.

    **IMPORTANT FLOW CHANGE:**
    This tool now CREATES THE ORDER after shipping selection!
    The order is saved with 'pending' payment status.
    User can pay later from "My Orders" page.

    **USE THIS WHEN:**
    - User selects a delivery method
    - User says "standard delivery", "pickup", "express"

    **METHOD CODES:**
    - pickup: Store pickup (free)
    - standard: Standard delivery (2-3 days)
    - express: Express delivery (next day)

    **WHAT THIS TOOL DOES:**
    1. Validates shipping method
    2. Calculates shipping cost
    3. **CREATES THE ORDER** (saves to database)
    4. Clears the cart
    5. Shows order number and payment options

    **AFTER USING THIS TOOL:**
    - Order is created and saved (with order number)
    - Cart is cleared
    - Payment status is 'pending'
    - User can choose to pay now OR pay later from "My Orders"

    Returns: Order created with payment options
    """
    args_schema: type[BaseModel] = SelectShippingMethodInput

    def _run(self, session_id: str, shipping_method: str) -> str:
        """Select shipping method, create order immediately, show payment options"""
        checkout_service = get_checkout_service()
        shipping_service = get_shipping_service()
        payment_service = get_payment_service()

        checkout = checkout_service.get_checkout_session(session_id)
        if not checkout:
            return "❌ No checkout session found."

        # Validate shipping method
        address = checkout.get('shipping_address', {})
        city = address.get('city', '')

        is_valid, error = shipping_service.validate_shipping_method(shipping_method, city)
        if not is_valid:
            return f"❌ {error}"

        # Calculate shipping cost
        cart_total = Decimal(checkout['cart_total'])
        shipping_cost = shipping_service.calculate_shipping_cost(
            shipping_method, cart_total
        )

        # Update checkout session
        checkout_service.update_checkout_session(session_id, {
            'shipping_method': shipping_method,
            'shipping_cost': str(shipping_cost),
            'status': 'shipping_selected'
        })

        # **CREATE ORDER IMMEDIATELY** - This is the key change!
        try:
            # Get or create customer from address info
            customer = checkout_service.get_or_create_customer(
                name=address.get('recipient_name', 'Guest'),
                phone=address.get('phone_number', ''),
                email=None
            )

            # Create shipping address
            shipping_address = checkout_service.save_shipping_address(address)

            # Create order
            order = checkout_service.create_order_from_cart(
                session_id=session_id,
                customer=customer,
                shipping_address=shipping_address,
                shipping_cost=shipping_cost
            )

            # Calculate minimum payment
            minimum_payment = order.minimum_required_amount

            # Get payment methods (filtered by minimum payment)
            payment_methods = payment_service.get_available_payment_methods(
                order.total_price,
                minimum_payment=minimum_payment
            )

            # Format response
            method_info = shipping_service.get_shipping_method(shipping_method)
            result = f"✅ **Order #{order.id} Created!**\n\n"
            result += f"🚚 {method_info['name']} - "
            result += f"FREE\n" if shipping_cost == 0 else f"UGX {shipping_cost:,.0f}\n"
            result += f"⏱️ Delivery: {method_info['delivery_time']}\n\n"

            result += f"📦 **Order Summary:**\n"
            result += f"Subtotal: UGX {order.subtotal:,.0f}\n"
            result += f"Shipping: UGX {order.shipping_cost:,.0f}\n"
            result += f"**Total: UGX {order.total_price:,.0f}**\n\n"

            # Show minimum payment requirement if > 0
            if minimum_payment > 0:
                result += f"💡 **Minimum Payment Required:** UGX {minimum_payment:,.0f}\n"
                result += f"   (This is the minimum amount needed to start production)\n"
                result += f"   Remaining balance: UGX {(order.total_price - minimum_payment):,.0f}\n\n"

            result += f"✅ Your order is saved! You can pay now or pay later from 'My Orders' page.\n\n"
            result += payment_service.format_payment_methods_message(payment_methods, minimum_payment)
            result += f"\n\nHow would you like to pay? (Or you can pay later from My Orders)"

            return result

        except Exception as e:
            return f"❌ Error creating order: {str(e)}"

    def _arun(self, session_id: str, shipping_method: str):
        raise NotImplementedError("Async not supported")


class CreateOrderTool(BaseTool):
    """DEPRECATED: Order is now created automatically by select_shipping_method tool"""
    name: str = "create_order"
    description: str = """
    **DEPRECATED: DO NOT USE THIS TOOL!**

    Orders are now created AUTOMATICALLY when user selects shipping method.
    The `select_shipping_method` tool handles order creation.

    **WHAT HAPPENED:**
    - Old flow: select_shipping → create_order → generate_payment
    - New flow: select_shipping (creates order) → generate_payment

    **IF YOU SEE THIS:**
    You should NOT be using this tool anymore!
    The order is already created after shipping selection.

    Use `generate_payment_link` tool directly after `select_shipping_method`.

    Returns: Error message explaining this tool is deprecated
    """
    args_schema: type[BaseModel] = CreateOrderInput

    def _run(self, session_id: str, customer_name: str, customer_phone: str,
             customer_email: Optional[str] = None) -> str:
        """DEPRECATED - Return error message"""
        return """❌ **This tool is deprecated!**

The order has already been created when you selected the shipping method.
The `select_shipping_method` tool now handles order creation automatically.

**What you should do:**
If user wants to pay now, use the `generate_payment_link` tool directly.
The order_id is already saved in the checkout session.

**New checkout flow:**
1. initiate_checkout
2. collect_shipping_address
3. select_shipping_method ← **ORDER CREATED HERE!**
4. generate_payment_link ← Use this next (if user wants to pay now)

No need to call create_order separately!"""

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")


class GeneratePaymentLinkTool(BaseTool):
    """Generate payment link or USSD code"""
    name: str = "generate_payment_link"
    description: str = """
    Generate payment link or USSD code for the order.

    **USE THIS WHEN:**
    - User selects payment method
    - Order is already created

    **PAYMENT METHOD CODES:**
    - stripe: Credit/Debit Card - Generates secure Stripe payment link
    - mtn_mobile_money: MTN Mobile Money - Triggers USSD prompt on user's phone
    - airtel_money: Airtel Money - Triggers USSD prompt on user's phone
    - cash_on_delivery: Cash on Delivery - Only available when no minimum payment required

    **NOTE:** For MTN/Airtel, the system will:
    1. Call provider API with phone number and amount
    2. Provider sends USSD prompt to user's phone
    3. User confirms payment on their phone
    4. System receives confirmation from provider

    Returns: Payment link or USSD instructions
    """
    args_schema: type[BaseModel] = GeneratePaymentLinkInput

    def _run(self, session_id: str, payment_method: str) -> str:
        """Generate payment link/instructions"""
        checkout_service = get_checkout_service()
        payment_service = get_payment_service()

        checkout = checkout_service.get_checkout_session(session_id)
        if not checkout:
            return "❌ No checkout session found."

        order_id = checkout.get('order_id')
        if not order_id:
            return "❌ Order not created yet. Please create order first."

        try:
            # Get order details
            order_summary = checkout_service.get_order_summary(order_id)
            order_total = Decimal(str(order_summary['total_price']))

            # Validate payment method
            is_valid, error = payment_service.validate_payment_method(
                payment_method, order_total
            )
            if not is_valid:
                return f"❌ {error}"

            result = f"💳 **Payment for Order #{order_id}**\n\n"

            # Handle different payment methods
            if payment_method == 'stripe':
                # Generate Stripe checkout link
                try:
                    payment_url = payment_service.create_stripe_checkout_session(order_id)
                    result += f"✅ **Card Payment Link Generated!**\n\n"
                    result += f"Click here to pay with card:\n{payment_url}\n\n"
                    result += f"Amount: UGX {order_total:,.0f}\n"
                    result += f"Secure payment powered by Stripe 🔒"
                except ValueError as e:
                    result += f"❌ {str(e)}\n\n"
                    result += f"Stripe is not configured. Please choose another payment method."

            elif payment_method in ['mtn_mobile_money', 'airtel_money']:
                # Generate mobile money instructions
                phone = order_summary['customer_phone']
                instructions = payment_service.generate_mobile_money_instructions(
                    provider=payment_method,
                    order_id=order_id,
                    phone_number=phone,
                    amount=order_total
                )

                result += f"📱 **{instructions['provider']} Payment**\n\n"
                result += f"🔢 USSD Code: **{instructions['ussd_code']}**\n\n"
                result += f"Amount: UGX {instructions['amount']:,.0f}\n\n"
                result += f"**Steps:**\n"
                for step in instructions['steps']:
                    result += f"{step}\n"

            elif payment_method == 'cash_on_delivery':
                result += f"💵 **Cash on Delivery Selected**\n\n"
                result += f"Amount to pay: UGX {order_total:,.0f}\n\n"
                result += f"✅ Your order is confirmed!\n"
                result += f"Pay cash when you receive your delivery.\n\n"
                result += f"Delivery address:\n{order_summary['shipping_address']['address_line1']}\n"
                result += f"{order_summary['shipping_address']['city']}"

            else:
                return f"❌ Invalid payment method: {payment_method}"

            # Delete checkout session after payment generation
            checkout_service.delete_checkout_session(session_id)

            result += f"\n\n📧 Order confirmation will be sent to: {order_summary['customer_phone']}"

            return result

        except ValueError as e:
            return f"❌ Error: {str(e)}"
        except Exception as e:
            return f"❌ Failed to generate payment: {str(e)}"

    def _arun(self, session_id: str, payment_method: str):
        raise NotImplementedError("Async not supported")


# Export all tools
def get_all_tools() -> List[BaseTool]:
    """
    Get all available tools for the LangChain agent.
    These tools are dynamically powered by Django models!
    """
    return [
        # Product discovery tools
        SearchProductsTool(),
        SearchCategoriesTool(),
        ValidateConfigurationTool(),
        GetPartOptionsTool(),
        GetAvailableCategoriesTool(),
        GetPriceRangeTool(),

        # Cart action tools (Phase 3 - Enable autonomous shopping!)
        AddToCartTool(),
        ViewCartTool(),
        RemoveFromCartTool(),
        UpdateCartQuantityTool(),

        # Checkout tools (Phase 4 - Enable conversational checkout!)
        InitiateCheckoutTool(),
        CollectShippingAddressTool(),
        GetShippingOptionsTool(),
        SelectShippingMethodTool(),
        CreateOrderTool(),
        GeneratePaymentLinkTool()
    ]
