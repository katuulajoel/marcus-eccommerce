"""
Payment Service - Manages payment methods and payment link generation
"""

import os
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from django.conf import settings

# Payment methods configuration
PAYMENT_METHODS = {
    'stripe': {
        'code': 'stripe',
        'name': 'Credit/Debit Card',
        'description': 'Pay securely with card via Stripe',
        'currencies': ['UGX', 'USD', 'EUR', 'GBP'],
        'min_amount': Decimal('1000'),  # UGX
        'icon': '💳',
        'enabled': True  # Will check for Stripe keys
    },
    'mtn_mobile_money': {
        'code': 'mtn_mobile_money',
        'name': 'MTN Mobile Money',
        'description': 'Pay with MTN Mobile Money (Uganda)',
        'currencies': ['UGX'],
        'min_amount': Decimal('500'),
        'icon': '📱',
        'ussd_code': '*165*3#',
        'enabled': True
    },
    'airtel_money': {
        'code': 'airtel_money',
        'name': 'Airtel Money',
        'description': 'Pay with Airtel Money (Uganda)',
        'currencies': ['UGX'],
        'min_amount': Decimal('500'),
        'icon': '📱',
        'ussd_code': '*185*9#',
        'enabled': True
    },
    'cash_on_delivery': {
        'code': 'cash_on_delivery',
        'name': 'Cash on Delivery',
        'description': 'Pay when you receive your order',
        'currencies': ['UGX'],
        'min_amount': Decimal('0'),
        'icon': '💵',
        'enabled': True
    }
}


class PaymentService:
    """Service for managing payment methods and generating payment links"""

    def __init__(self):
        # Check if Stripe is configured
        self.stripe_enabled = bool(
            getattr(settings, 'STRIPE_SECRET_KEY', None) and
            getattr(settings, 'STRIPE_PUBLISHABLE_KEY', None)
        )

        # Disable Stripe payment method if not configured
        if not self.stripe_enabled:
            PAYMENT_METHODS['stripe']['enabled'] = False

    def get_all_payment_methods(self) -> List[Dict]:
        """
        Get all payment methods

        Returns:
            list: List of payment method configurations
        """
        return [method for method in PAYMENT_METHODS.values() if method['enabled']]

    def get_payment_method(self, method_code: str) -> Optional[Dict]:
        """
        Get specific payment method by code

        Args:
            method_code: Payment method code

        Returns:
            dict: Payment method configuration or None
        """
        method = PAYMENT_METHODS.get(method_code)
        if method and method['enabled']:
            return method
        return None

    def get_available_payment_methods(
        self,
        order_total: Decimal,
        currency: str = 'UGX',
        minimum_payment: Decimal = None
    ) -> List[Dict]:
        """
        Get available payment methods for an order

        Args:
            order_total: Order total amount
            currency: Currency code
            minimum_payment: Minimum payment required (optional)

        Returns:
            list: Available payment methods
        """
        available_methods = []

        # If no minimum payment specified, default to 0
        if minimum_payment is None:
            minimum_payment = Decimal('0.00')

        for method in self.get_all_payment_methods():
            # Check if method supports currency
            if currency not in method['currencies']:
                continue

            # Check if order meets minimum amount
            if order_total < method['min_amount']:
                continue

            # Cash on Delivery: Only available if minimum payment is 0
            if method['code'] == 'cash_on_delivery' and minimum_payment > 0:
                continue

            # Build method info
            method_info = {
                'code': method['code'],
                'name': method['name'],
                'description': method['description'],
                'icon': method['icon']
            }

            # Add USSD code for mobile money
            if 'ussd_code' in method:
                method_info['ussd_code'] = method['ussd_code']

            available_methods.append(method_info)

        return available_methods

    def validate_payment_method(
        self,
        method_code: str,
        order_total: Decimal,
        currency: str = 'UGX'
    ) -> Tuple[bool, str]:
        """
        Validate payment method for an order

        Args:
            method_code: Payment method code
            order_total: Order total amount
            currency: Currency code

        Returns:
            tuple: (is_valid, error_message)
        """
        method = self.get_payment_method(method_code)

        if not method:
            return False, f"Payment method '{method_code}' is not available"

        if currency not in method['currencies']:
            return False, f"{method['name']} does not support {currency}"

        if order_total < method['min_amount']:
            return False, f"Minimum amount for {method['name']} is {method['min_amount']} {currency}"

        return True, ""

    # ========== Stripe Integration ==========

    def create_stripe_checkout_session(self, order_id: int) -> str:
        """
        Create Stripe checkout session and return payment URL

        Args:
            order_id: Order ID

        Returns:
            str: Stripe checkout URL

        Raises:
            ValueError: If Stripe is not configured or order not found
        """
        if not self.stripe_enabled:
            raise ValueError("Stripe is not configured. Please set STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY")

        try:
            import stripe
            from apps.orders.models import Orders

            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Get order
            order = Orders.objects.select_related('customer', 'shipping_address').get(id=order_id)

            # Create line items
            line_items = []

            # Add products
            for order_product in order.products.all():
                line_items.append({
                    'price_data': {
                        'currency': order.order_currency.lower(),
                        'product_data': {
                            'name': order_product.base_product_name,
                        },
                        'unit_amount': int(order.subtotal * 100),  # Convert to cents
                    },
                    'quantity': 1,
                })

            # Add shipping as separate line item
            if order.shipping_cost > 0:
                line_items.append({
                    'price_data': {
                        'currency': order.order_currency.lower(),
                        'product_data': {
                            'name': 'Shipping',
                        },
                        'unit_amount': int(order.shipping_cost * 100),
                    },
                    'quantity': 1,
                })

            # Create Stripe checkout session
            success_url = f"{settings.FRONTEND_URL}/order-confirmation?order_id={order_id}&session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{settings.FRONTEND_URL}/cart"

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=order.customer.email if order.customer.email else None,
                metadata={
                    'order_id': order_id
                }
            )

            return session.url

        except Orders.DoesNotExist:
            raise ValueError(f"Order {order_id} not found")
        except Exception as e:
            raise ValueError(f"Failed to create Stripe session: {str(e)}")

    # ========== Mobile Money Integration ==========

    def generate_mobile_money_instructions(
        self,
        provider: str,
        order_id: int,
        phone_number: str,
        amount: Decimal
    ) -> Dict:
        """
        Generate mobile money payment instructions

        Args:
            provider: Provider code (mtn_mobile_money or airtel_money)
            order_id: Order ID
            phone_number: Customer phone number
            amount: Payment amount

        Returns:
            dict: Payment instructions with USSD code
        """
        method = self.get_payment_method(provider)

        if not method or 'ussd_code' not in method:
            raise ValueError(f"Invalid mobile money provider: {provider}")

        # Format instructions
        instructions = {
            'provider': method['name'],
            'ussd_code': method['ussd_code'],
            'amount': float(amount),
            'phone_number': phone_number,
            'order_id': order_id,
            'steps': self._get_mobile_money_steps(provider, amount)
        }

        return instructions

    def _get_mobile_money_steps(self, provider: str, amount: Decimal) -> List[str]:
        """Get step-by-step instructions for mobile money payment"""
        if provider == 'mtn_mobile_money':
            return [
                "1. We'll send a payment request to your MTN number",
                "2. You'll receive a USSD prompt on your phone",
                f"3. Confirm the amount: UGX {amount:,.0f}",
                "4. Enter your MTN Mobile Money PIN",
                "5. You'll receive a confirmation SMS",
                "6. Your order will be updated automatically"
            ]
        elif provider == 'airtel_money':
            return [
                "1. We'll send a payment request to your Airtel number",
                "2. You'll receive a USSD prompt on your phone",
                f"3. Confirm the amount: UGX {amount:,.0f}",
                "4. Enter your Airtel Money PIN",
                "5. You'll receive a confirmation SMS",
                "6. Your order will be updated automatically"
            ]
        else:
            return ["Please follow the USSD prompts to complete payment"]

    # ========== Helper Methods ==========

    def format_payment_methods_message(
        self,
        payment_methods: List[Dict],
        minimum_payment: Decimal = None
    ) -> str:
        """
        Format payment methods as user-friendly message

        Args:
            payment_methods: List of available payment methods
            minimum_payment: Minimum payment required (optional)

        Returns:
            str: Formatted message
        """
        if not payment_methods:
            return "❌ No payment methods available for this order."

        message_parts = ["💳 **Available Payment Methods:**\n"]

        for i, method in enumerate(payment_methods, 1):
            message_parts.append(
                f"{i}. {method['icon']} **{method['name']}**\n"
                f"   {method['description']}\n"
            )

        # Add note about Cash on Delivery availability
        if minimum_payment and minimum_payment > 0:
            has_cod = any(m['code'] == 'cash_on_delivery' for m in payment_methods)
            if not has_cod:
                message_parts.append(
                    "\nℹ️ Cash on Delivery is not available because this order requires a minimum upfront payment.\n"
                )

        return "\n".join(message_parts)


# Import Tuple at the top if not already imported
from typing import Tuple


# Singleton instance
_payment_service_instance = None

def get_payment_service() -> PaymentService:
    """Get singleton payment service instance"""
    global _payment_service_instance
    if _payment_service_instance is None:
        _payment_service_instance = PaymentService()
    return _payment_service_instance
