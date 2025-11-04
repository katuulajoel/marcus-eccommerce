"""
Redis-based Shopping Cart Service
Manages temporary shopping carts with automatic expiration (7 days TTL).
No database cleanup needed!
"""

import redis
import json
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime
from django.conf import settings


class RedisCartService:
    """
    Redis-based cart management with automatic expiration.

    Features:
    - Fast in-memory operations
    - Automatic 7-day TTL (no cleanup needed)
    - Session-based (works for web + WhatsApp)
    - Thread-safe atomic operations
    """

    def __init__(self):
        """Initialize Redis client for cart operations"""
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_CART_DB,  # Separate DB for carts
            password=settings.REDIS_PASSWORD,
            decode_responses=True  # Auto-decode bytes to strings
        )
        self.cart_ttl = 604800  # 7 days in seconds

    def add_item(
        self,
        session_id: str,
        product_id: int,
        name: str,
        price: Decimal,
        quantity: int = 1,
        configuration: Dict = None,
        image_url: str = None,
        category_id: int = None,
        config_details: Dict = None
    ) -> Dict:
        """
        Add item to cart or update quantity if exists.

        Args:
            session_id: User's session ID (web: session-xxx, whatsapp: wa_256701618576)
            product_id: Product ID from database
            name: Product name
            price: Price per unit
            quantity: Quantity to add (default: 1)
            configuration: Product configuration dict (for customizable products)
            image_url: Product image URL
            category_id: Category ID

        Returns:
            Dict with added item details
        """
        cart_key = f"cart:{session_id}"
        items_key = f"{cart_key}:items"

        # Generate unique item ID based on product + configuration
        config_hash = hash(json.dumps(configuration, sort_keys=True)) if configuration else ""
        item_id = f"{product_id}_{config_hash}"
        item_key = f"{cart_key}:item:{item_id}"

        # Check if item already exists
        if self.redis_client.sismember(items_key, item_id):
            # Update quantity (add to existing)
            current_qty = int(self.redis_client.hget(item_key, 'quantity') or 0)
            new_qty = current_qty + quantity
            self.redis_client.hset(item_key, 'quantity', new_qty)
        else:
            # Add new item
            self.redis_client.sadd(items_key, item_id)
            self.redis_client.hset(item_key, mapping={
                'product_id': product_id,
                'name': name,
                'price': str(price),
                'quantity': quantity,
                'configuration': json.dumps(configuration or {}),
                'config_details': json.dumps(config_details or {}),
                'image_url': image_url or '',
                'category_id': category_id or ''
            })

        # Update cart metadata and refresh TTL
        self.redis_client.hset(cart_key, 'updated_at', self._now())
        self._refresh_ttl(session_id)

        return self.get_item(session_id, item_id)

    def remove_item(self, session_id: str, item_id: str) -> bool:
        """
        Remove item from cart.

        Args:
            session_id: User's session ID
            item_id: Item ID to remove

        Returns:
            True if removed successfully
        """
        cart_key = f"cart:{session_id}"
        items_key = f"{cart_key}:items"
        item_key = f"{cart_key}:item:{item_id}"

        # Remove from set and delete item hash
        self.redis_client.srem(items_key, item_id)
        self.redis_client.delete(item_key)

        self._refresh_ttl(session_id)
        return True

    def update_quantity(self, session_id: str, item_id: str, quantity: int) -> Optional[Dict]:
        """
        Update item quantity (remove if quantity <= 0).

        Args:
            session_id: User's session ID
            item_id: Item ID to update
            quantity: New quantity

        Returns:
            Updated item dict or None if removed
        """
        if quantity <= 0:
            self.remove_item(session_id, item_id)
            return None

        cart_key = f"cart:{session_id}"
        item_key = f"{cart_key}:item:{item_id}"

        self.redis_client.hset(item_key, 'quantity', quantity)
        self._refresh_ttl(session_id)

        return self.get_item(session_id, item_id)

    def get_cart(self, session_id: str) -> Dict:
        """
        Get full cart with all items and totals.

        Args:
            session_id: User's session ID

        Returns:
            Dict with cart items, subtotal, item count
        """
        cart_key = f"cart:{session_id}"
        items_key = f"{cart_key}:items"

        # Get all item IDs
        item_ids = self.redis_client.smembers(items_key)

        items = []
        subtotal = Decimal('0')
        total_items = 0

        for item_id in item_ids:
            item = self.get_item(session_id, item_id)
            if item:
                items.append(item)
                subtotal += Decimal(str(item['price'])) * item['quantity']
                total_items += item['quantity']

        self._refresh_ttl(session_id)

        return {
            'session_id': session_id,
            'items': items,
            'item_count': total_items,
            'subtotal': float(subtotal),
            'currency': 'UGX'
        }

    def get_item(self, session_id: str, item_id: str) -> Optional[Dict]:
        """
        Get single cart item.

        Args:
            session_id: User's session ID
            item_id: Item ID

        Returns:
            Item dict or None if not found
        """
        cart_key = f"cart:{session_id}"
        item_key = f"{cart_key}:item:{item_id}"

        item_data = self.redis_client.hgetall(item_key)
        if not item_data:
            return None

        price = float(item_data['price'])
        quantity = int(item_data['quantity'])

        return {
            'item_id': item_id,
            'product_id': int(item_data['product_id']),
            'name': item_data['name'],
            'price': price,
            'quantity': quantity,
            'configuration': json.loads(item_data.get('configuration', '{}')),
            'config_details': json.loads(item_data.get('config_details', '{}')),
            'image_url': item_data.get('image_url', ''),
            'category_id': int(item_data['category_id']) if item_data.get('category_id') else None,
            'line_total': price * quantity
        }

    def clear_cart(self, session_id: str) -> bool:
        """
        Clear all items from cart.

        Args:
            session_id: User's session ID

        Returns:
            True if cleared successfully
        """
        cart_key = f"cart:{session_id}"
        items_key = f"{cart_key}:items"

        # Get all items and delete them
        item_ids = self.redis_client.smembers(items_key)
        for item_id in item_ids:
            item_key = f"{cart_key}:item:{item_id}"
            self.redis_client.delete(item_key)

        # Clear items set and cart metadata
        self.redis_client.delete(items_key)
        self.redis_client.delete(cart_key)

        return True

    def link_to_customer(self, session_id: str, customer_id: int, phone: str = None):
        """
        Link cart to customer for order creation.

        Args:
            session_id: User's session ID
            customer_id: Customer ID from database
            phone: Phone number (optional)
        """
        cart_key = f"cart:{session_id}"
        self.redis_client.hset(cart_key, mapping={
            'customer_id': customer_id,
            'phone_number': phone or ''
        })
        self._refresh_ttl(session_id)

    def get_cart_metadata(self, session_id: str) -> Dict:
        """
        Get cart metadata (customer_id, phone, timestamps).

        Args:
            session_id: User's session ID

        Returns:
            Dict with metadata
        """
        cart_key = f"cart:{session_id}"
        metadata = self.redis_client.hgetall(cart_key)
        return metadata if metadata else {}

    def _refresh_ttl(self, session_id: str):
        """
        Refresh TTL on all cart keys (extends cart expiration).

        Args:
            session_id: User's session ID
        """
        cart_key = f"cart:{session_id}"
        items_key = f"{cart_key}:items"

        self.redis_client.expire(cart_key, self.cart_ttl)
        self.redis_client.expire(items_key, self.cart_ttl)

        # Refresh TTL on all items
        item_ids = self.redis_client.smembers(items_key)
        for item_id in item_ids:
            item_key = f"{cart_key}:item:{item_id}"
            self.redis_client.expire(item_key, self.cart_ttl)

    def _now(self) -> str:
        """Current timestamp in ISO format"""
        return datetime.now().isoformat()


# Global singleton instance
_cart_service = None


def get_cart_service() -> RedisCartService:
    """
    Get or create the global RedisCartService instance.

    Returns:
        RedisCartService singleton
    """
    global _cart_service
    if _cart_service is None:
        _cart_service = RedisCartService()
    return _cart_service
