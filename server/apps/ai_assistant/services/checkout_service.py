"""
Checkout Service - Manages checkout sessions and orchestrates checkout flow
"""

import redis
import json
from decimal import Decimal
from typing import Dict, Tuple, Optional, List
from datetime import datetime
from django.conf import settings
from django.db import transaction

from apps.orders.models import Orders, OrderProduct, OrderItem, ShippingAddress
from apps.customers.models import Customer
from apps.products.models import PartOption
from apps.preconfigured_products.models import PreConfiguredProduct
from .cart_service import get_cart_service


class CheckoutService:
    """Service for managing checkout sessions and order creation"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_CART_DB,  # Use same DB as cart (DB 1)
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        self.cart_service = get_cart_service()
        self.checkout_ttl = 3600  # 1 hour

    # ========== Session Management ==========

    def create_checkout_session(self, session_id: str) -> Dict:
        """
        Create a new checkout session

        Args:
            session_id: User's session ID

        Returns:
            dict: Checkout session data
        """
        # Verify cart exists and has items
        cart = self.cart_service.get_cart(session_id)
        if not cart.get('items') or cart.get('item_count', 0) == 0:
            raise ValueError("Cannot checkout with empty cart")

        checkout_data = {
            'session_id': session_id,
            'status': 'collecting_address',
            'cart_total': str(cart.get('subtotal', 0)),
            'item_count': cart.get('item_count', 0),
            'customer': {},
            'shipping_address': {},
            'shipping_method': None,
            'shipping_cost': '0',
            'order_id': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        # Store in Redis
        key = f"checkout:{session_id}"
        self.redis_client.setex(
            key,
            self.checkout_ttl,
            json.dumps(checkout_data)
        )

        return checkout_data

    def get_checkout_session(self, session_id: str) -> Optional[Dict]:
        """Get existing checkout session"""
        key = f"checkout:{session_id}"
        data = self.redis_client.get(key)

        if not data:
            return None

        return json.loads(data)

    def update_checkout_session(self, session_id: str, updates: Dict) -> Dict:
        """
        Update checkout session with new data

        Args:
            session_id: User's session ID
            updates: Dictionary of fields to update

        Returns:
            dict: Updated checkout session
        """
        checkout = self.get_checkout_session(session_id)
        if not checkout:
            raise ValueError(f"Checkout session not found for {session_id}")

        # Update fields
        checkout.update(updates)
        checkout['updated_at'] = datetime.now().isoformat()

        # Save back to Redis
        key = f"checkout:{session_id}"
        self.redis_client.setex(
            key,
            self.checkout_ttl,
            json.dumps(checkout)
        )

        return checkout

    def delete_checkout_session(self, session_id: str):
        """Delete checkout session"""
        key = f"checkout:{session_id}"
        self.redis_client.delete(key)

    # ========== Address Handling ==========

    def validate_address(self, address_data: Dict) -> Tuple[bool, str]:
        """
        Validate shipping address data

        Args:
            address_data: Dictionary with address fields

        Returns:
            tuple: (is_valid, error_message)
        """
        required_fields = ['recipient_name', 'phone_number', 'address_line1', 'city']

        # Check required fields
        for field in required_fields:
            if not address_data.get(field):
                return False, f"Missing required field: {field}"

        # Validate phone number format
        phone = address_data.get('phone_number', '')
        if not phone.startswith('+'):
            return False, "Phone number must start with country code (e.g., +256)"

        if len(phone) < 10:
            return False, "Phone number is too short"

        # Validate name
        name = address_data.get('recipient_name', '')
        if len(name) < 2:
            return False, "Recipient name is too short"

        # Validate address
        address = address_data.get('address_line1', '')
        if len(address) < 5:
            return False, "Address is too short"

        # Validate city
        city = address_data.get('city', '')
        if len(city) < 2:
            return False, "City name is too short"

        return True, ""

    def save_shipping_address(self, address_data: Dict) -> ShippingAddress:
        """
        Save shipping address to database

        Args:
            address_data: Dictionary with address fields

        Returns:
            ShippingAddress: Saved address object
        """
        # Validate first
        is_valid, error = self.validate_address(address_data)
        if not is_valid:
            raise ValueError(error)

        # Create and save address
        address = ShippingAddress.objects.create(
            recipient_name=address_data['recipient_name'],
            phone_number=address_data['phone_number'],
            address_line1=address_data['address_line1'],
            address_line2=address_data.get('address_line2', ''),
            city=address_data['city'],
            state_province=address_data.get('state_province', ''),
            postal_code=address_data.get('postal_code', ''),
            country=address_data.get('country', 'Uganda')
        )

        return address

    # ========== Customer Handling ==========

    def calculate_minimum_payment_from_cart(self, session_id: str) -> Decimal:
        """
        Calculate minimum payment required from cart items BEFORE order creation

        Args:
            session_id: User's session ID

        Returns:
            Decimal: Total minimum payment required
        """
        cart = self.cart_service.get_cart(session_id)
        if not cart.get('items'):
            return Decimal('0.00')

        total_minimum = Decimal('0.00')

        for cart_item in cart['items']:
            configuration = cart_item.get('configuration', {})

            # For configured products, sum up minimum payments from each part
            if configuration and isinstance(configuration, dict):
                for part_name, option_data in configuration.items():
                    option_id = option_data.get('id') if isinstance(option_data, dict) else option_data

                    if option_id:
                        try:
                            part_option = PartOption.objects.get(id=option_id)
                            # Calculate minimum payment for this part option
                            min_payment = part_option.default_price * part_option.minimum_payment_percentage
                            total_minimum += min_payment
                        except PartOption.DoesNotExist:
                            continue
            else:
                # For simple products without configuration, assume no minimum requirement
                # (or you could add minimum_payment field to PreConfiguredProduct in the future)
                pass

        return total_minimum

    def get_or_create_customer(self, name: str, phone: str, email: str = None) -> Customer:
        """
        Get existing customer or create new one (guest checkout)

        Args:
            name: Customer name
            phone: Customer phone number
            email: Customer email (optional)

        Returns:
            Customer: Customer object
        """
        # Try to find existing customer by phone
        customer = None
        if phone:
            customer = Customer.objects.filter(phone=phone).first()

        # Or by email
        if not customer and email:
            customer = Customer.objects.filter(email=email).first()

        # Create new customer if not found
        if not customer:
            customer = Customer.objects.create(
                name=name,
                phone=phone,
                email=email
            )

        return customer

    # ========== Order Creation ==========

    @transaction.atomic
    def create_order_from_cart(
        self,
        session_id: str,
        customer: Customer,
        shipping_address: ShippingAddress,
        shipping_cost: Decimal,
        currency: str = 'UGX'
    ) -> Orders:
        """
        Create order in PostgreSQL from Redis cart

        Args:
            session_id: User's session ID
            customer: Customer object
            shipping_address: ShippingAddress object
            shipping_cost: Shipping cost
            currency: Order currency (default: UGX)

        Returns:
            Orders: Created order object
        """
        # Get cart data
        cart = self.cart_service.get_cart(session_id)
        if not cart.get('items'):
            raise ValueError("Cannot create order from empty cart")

        cart_items = cart['items']
        subtotal = Decimal(str(cart.get('subtotal', 0)))
        total_price = subtotal + shipping_cost

        # Create order
        order = Orders.objects.create(
            customer=customer,
            shipping_address=shipping_address,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total_price=total_price,
            order_currency=currency,
            payment_status='pending',
            fulfillment_status='pending'
        )

        # Create order products and items
        for cart_item in cart_items:
            # Try to find preconfigured product if it exists
            preconfigured_product = None
            product_id = cart_item.get('product_id')

            if product_id:
                try:
                    preconfigured_product = PreConfiguredProduct.objects.get(id=product_id)
                except PreConfiguredProduct.DoesNotExist:
                    pass

            # Create OrderProduct
            order_product = OrderProduct.objects.create(
                order=order,
                preconfigured_product=preconfigured_product,
                base_product_name=cart_item.get('name', 'Custom Product')
            )

            # For configured products, create OrderItems for each part
            configuration = cart_item.get('configuration', {})
            if configuration and isinstance(configuration, dict):
                for part_name, option_data in configuration.items():
                    # Get option details
                    option_id = option_data.get('id') if isinstance(option_data, dict) else option_data

                    try:
                        if option_id:
                            part_option = PartOption.objects.get(id=option_id)

                            # Calculate minimum payment required based on percentage
                            min_payment = part_option.default_price * part_option.minimum_payment_percentage

                            OrderItem.objects.create(
                                order_product=order_product,
                                part_name=part_name,
                                option_name=part_option.name,
                                final_price=part_option.default_price,
                                minimum_payment_required=min_payment
                            )
                    except PartOption.DoesNotExist:
                        # Skip if part option not found
                        continue
            else:
                # For simple products without configuration, create a single OrderItem
                unit_price = Decimal(str(cart_item.get('price', 0)))
                quantity = cart_item.get('quantity', 1)

                OrderItem.objects.create(
                    order_product=order_product,
                    part_name='Product',
                    option_name=cart_item.get('name', 'Item'),
                    final_price=unit_price * quantity,
                    minimum_payment_required=Decimal('0.00')
                )

        # Calculate minimum required amount
        minimum_required = order.calculate_minimum_required_amount()
        order.minimum_required_amount = minimum_required
        order.save()

        # Update checkout session with order ID
        self.update_checkout_session(session_id, {
            'order_id': order.id,
            'status': 'order_created'
        })

        # Clear the cart after successful order creation
        self.cart_service.clear_cart(session_id)

        return order

    def get_order_summary(self, order_id: int) -> Dict:
        """
        Get order summary for display

        Args:
            order_id: Order ID

        Returns:
            dict: Order summary data
        """
        try:
            order = Orders.objects.select_related('customer', 'shipping_address').get(id=order_id)

            return {
                'order_id': order.id,
                'customer_name': order.customer.name,
                'customer_phone': order.customer.phone,
                'shipping_address': {
                    'recipient_name': order.shipping_address.recipient_name,
                    'address_line1': order.shipping_address.address_line1,
                    'city': order.shipping_address.city,
                    'phone_number': order.shipping_address.phone_number
                },
                'subtotal': float(order.subtotal),
                'shipping_cost': float(order.shipping_cost),
                'total_price': float(order.total_price),
                'currency': order.order_currency,
                'payment_status': order.payment_status,
                'fulfillment_status': order.fulfillment_status,
                'created_at': order.created_at.isoformat()
            }
        except Orders.DoesNotExist:
            raise ValueError(f"Order {order_id} not found")


# Singleton instance
_checkout_service_instance = None

def get_checkout_service() -> CheckoutService:
    """Get singleton checkout service instance"""
    global _checkout_service_instance
    if _checkout_service_instance is None:
        _checkout_service_instance = CheckoutService()
    return _checkout_service_instance
