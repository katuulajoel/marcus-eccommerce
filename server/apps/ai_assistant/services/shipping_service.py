"""
Shipping Service - Manages shipping methods and cost calculation
"""

from decimal import Decimal
from typing import List, Dict, Optional, Tuple


# Shipping methods configuration
SHIPPING_METHODS = {
    'pickup': {
        'code': 'pickup',
        'name': 'Store Pickup',
        'description': 'Pick up from our Kampala store (Free)',
        'base_cost': Decimal('0'),
        'delivery_time': 'Same day',
        'available_cities': ['Kampala', 'Entebbe'],
        'free_threshold': Decimal('0'),  # Always free
        'icon': '🏪'
    },
    'standard': {
        'code': 'standard',
        'name': 'Standard Delivery',
        'description': 'Delivery within 2-3 business days',
        'base_cost': Decimal('15000'),  # UGX
        'delivery_time': '2-3 days',
        'available_cities': ['Kampala', 'Entebbe', 'Jinja', 'Mbarara', 'Gulu', 'Masaka', 'Mbale'],
        'free_threshold': Decimal('500000'),  # Free shipping on orders > 500k UGX
        'icon': '🚚'
    },
    'express': {
        'code': 'express',
        'name': 'Express Delivery',
        'description': 'Next-day delivery',
        'base_cost': Decimal('30000'),  # UGX
        'delivery_time': 'Next day',
        'available_cities': ['Kampala', 'Entebbe'],
        'free_threshold': Decimal('1000000'),  # Free express on orders > 1M UGX
        'icon': '⚡'
    }
}


class ShippingService:
    """Service for managing shipping methods and calculating shipping costs"""

    def get_all_shipping_methods(self) -> List[Dict]:
        """
        Get all available shipping methods

        Returns:
            list: List of shipping method configurations
        """
        return list(SHIPPING_METHODS.values())

    def get_shipping_method(self, method_code: str) -> Optional[Dict]:
        """
        Get specific shipping method by code

        Args:
            method_code: Shipping method code (pickup, standard, express)

        Returns:
            dict: Shipping method configuration or None
        """
        return SHIPPING_METHODS.get(method_code)

    def get_available_shipping_methods(
        self,
        cart_total: Decimal,
        city: str,
        currency: str = 'UGX'
    ) -> List[Dict]:
        """
        Get available shipping methods for a specific city and cart total

        Args:
            cart_total: Cart subtotal
            city: Delivery city
            currency: Currency code (default: UGX)

        Returns:
            list: Available shipping methods with calculated costs
        """
        available_methods = []

        for method_code, method_config in SHIPPING_METHODS.items():
            # Check if method is available in the city
            if city not in method_config['available_cities']:
                continue

            # Calculate shipping cost
            shipping_cost = self.calculate_shipping_cost(
                method_code=method_code,
                cart_total=cart_total,
                currency=currency
            )

            # Build method info
            method_info = {
                'code': method_config['code'],
                'name': method_config['name'],
                'description': method_config['description'],
                'cost': float(shipping_cost),
                'delivery_time': method_config['delivery_time'],
                'icon': method_config['icon'],
                'is_free': shipping_cost == Decimal('0')
            }

            available_methods.append(method_info)

        return available_methods

    def calculate_shipping_cost(
        self,
        method_code: str,
        cart_total: Decimal,
        currency: str = 'UGX'
    ) -> Decimal:
        """
        Calculate shipping cost for a specific method

        Args:
            method_code: Shipping method code
            cart_total: Cart subtotal
            currency: Currency code

        Returns:
            Decimal: Calculated shipping cost
        """
        method = self.get_shipping_method(method_code)
        if not method:
            raise ValueError(f"Invalid shipping method: {method_code}")

        # Pickup is always free
        if method_code == 'pickup':
            return Decimal('0')

        # Check if cart qualifies for free shipping
        if cart_total >= method['free_threshold']:
            return Decimal('0')

        # Return base cost
        # TODO: Add currency conversion if needed
        return method['base_cost']

    def validate_shipping_method(self, method_code: str, city: str) -> Tuple[bool, str]:
        """
        Validate that a shipping method is available for a city

        Args:
            method_code: Shipping method code
            city: Delivery city

        Returns:
            tuple: (is_valid, error_message)
        """
        method = self.get_shipping_method(method_code)

        if not method:
            return False, f"Invalid shipping method: {method_code}"

        if city not in method['available_cities']:
            return False, f"{method['name']} is not available in {city}"

        return True, ""

    def format_shipping_options_message(
        self,
        shipping_methods: List[Dict],
        cart_total: Decimal
    ) -> str:
        """
        Format shipping options as a user-friendly message

        Args:
            shipping_methods: List of available shipping methods
            cart_total: Cart subtotal

        Returns:
            str: Formatted message
        """
        if not shipping_methods:
            return "❌ Sorry, we don't deliver to your area yet."

        message_parts = ["🚚 **Available Delivery Options:**\n"]

        for i, method in enumerate(shipping_methods, 1):
            cost_str = "FREE" if method['is_free'] else f"UGX {method['cost']:,.0f}"

            message_parts.append(
                f"{i}. {method['icon']} **{method['name']}** - {cost_str}\n"
                f"   {method['description']}\n"
                f"   ⏱️ Delivery: {method['delivery_time']}\n"
            )

        # Add free shipping threshold message
        message_parts.append(
            f"\n💡 *Free standard delivery on orders over UGX 500,000!*"
        )

        return "\n".join(message_parts)


# Singleton instance
_shipping_service_instance = None

def get_shipping_service() -> ShippingService:
    """Get singleton shipping service instance"""
    global _shipping_service_instance
    if _shipping_service_instance is None:
        _shipping_service_instance = ShippingService()
    return _shipping_service_instance
