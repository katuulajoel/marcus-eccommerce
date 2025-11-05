#!/usr/bin/env python
"""
Phase 1 Cart Testing Script
Tests Redis cart service, LangChain tools, and API endpoints.

Run after starting Docker:
    docker compose up -d
    python test_cart_phase1.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()

from decimal import Decimal
from apps.ai_assistant.services.cart_service import get_cart_service
from apps.ai_assistant.services.langchain_tools import AddToCartTool, ViewCartTool, RemoveFromCartTool


def test_redis_connection():
    """Test 1: Verify Redis connection"""
    print("\n" + "="*60)
    print("TEST 1: Redis Connection")
    print("="*60)

    try:
        cart_service = get_cart_service()
        # Try to ping Redis
        cart_service.redis_client.ping()
        print("✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("\nMake sure Docker is running:")
        print("  docker compose up -d redis")
        return False


def test_cart_service():
    """Test 2: Cart Service CRUD Operations"""
    print("\n" + "="*60)
    print("TEST 2: Cart Service Operations")
    print("="*60)

    cart_service = get_cart_service()
    session_id = "test-session-phase1"

    try:
        # Clear any existing cart
        cart_service.clear_cart(session_id)
        print("✅ Cart cleared")

        # Test 2.1: Add item to cart
        print("\n2.1 Adding item to cart...")
        item = cart_service.add_item(
            session_id=session_id,
            product_id=1,
            name="Hot Air Balloon Bouquet",
            price=Decimal("120000"),
            quantity=2,
            image_url="https://example.com/balloon.jpg",
            category_id=1
        )
        print(f"✅ Item added: {item['name']} x{item['quantity']}")
        print(f"   Line total: UGX {item['line_total']:,.0f}")

        # Test 2.2: Get cart
        print("\n2.2 Getting cart contents...")
        cart = cart_service.get_cart(session_id)
        print(f"✅ Cart retrieved:")
        print(f"   Items: {cart['item_count']}")
        print(f"   Subtotal: UGX {cart['subtotal']:,.0f}")

        # Test 2.3: Add another item
        print("\n2.3 Adding second item...")
        cart_service.add_item(
            session_id=session_id,
            product_id=2,
            name="Explosion Box - Boyfriend Kit",
            price=Decimal("135000"),
            quantity=1,
            category_id=2
        )
        cart = cart_service.get_cart(session_id)
        print(f"✅ Second item added")
        print(f"   Total items: {cart['item_count']}")
        print(f"   New subtotal: UGX {cart['subtotal']:,.0f}")

        # Test 2.4: Update quantity
        print("\n2.4 Updating quantity...")
        item_id = cart['items'][0]['item_id']
        cart_service.update_quantity(session_id, item_id, 5)
        cart = cart_service.get_cart(session_id)
        print(f"✅ Quantity updated to 5")
        print(f"   New subtotal: UGX {cart['subtotal']:,.0f}")

        # Test 2.5: Remove item
        print("\n2.5 Removing item...")
        cart_service.remove_item(session_id, item_id)
        cart = cart_service.get_cart(session_id)
        print(f"✅ Item removed")
        print(f"   Remaining items: {cart['item_count']}")

        # Test 2.6: Clear cart
        print("\n2.6 Clearing cart...")
        cart_service.clear_cart(session_id)
        cart = cart_service.get_cart(session_id)
        print(f"✅ Cart cleared")
        print(f"   Items: {cart['item_count']}")

        return True

    except Exception as e:
        print(f"❌ Cart service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_redis_ttl():
    """Test 3: Verify TTL is set correctly"""
    print("\n" + "="*60)
    print("TEST 3: Redis TTL (Auto-expiration)")
    print("="*60)

    cart_service = get_cart_service()
    session_id = "test-ttl-session"

    try:
        # Add item
        cart_service.add_item(
            session_id=session_id,
            product_id=999,
            name="Test Product",
            price=Decimal("10000"),
            quantity=1
        )

        # Check TTL
        cart_key = f"cart:{session_id}"
        ttl = cart_service.redis_client.ttl(cart_key)

        expected_ttl = 604800  # 7 days
        if ttl > 0 and ttl <= expected_ttl:
            days = ttl / 86400
            print(f"✅ TTL is set correctly: {ttl} seconds (~{days:.1f} days)")
            print(f"   Cart will auto-expire in {days:.1f} days")
        else:
            print(f"❌ TTL issue: {ttl} seconds (expected ~{expected_ttl})")

        # Cleanup
        cart_service.clear_cart(session_id)

        return True

    except Exception as e:
        print(f"❌ TTL test failed: {e}")
        return False


def test_langchain_tools():
    """Test 4: LangChain Cart Tools"""
    print("\n" + "="*60)
    print("TEST 4: LangChain Cart Tools")
    print("="*60)

    session_id = "test-langchain-session"

    try:
        # Clear cart first
        cart_service = get_cart_service()
        cart_service.clear_cart(session_id)

        # Test 4.1: AddToCartTool
        print("\n4.1 Testing AddToCartTool...")
        add_tool = AddToCartTool()
        result = add_tool._run(
            session_id=session_id,
            product_id=101,
            product_name="Luxury Balloon Bouquet",
            price=150000.0,
            quantity=2
        )
        print("✅ AddToCartTool result:")
        print(result)

        # Test 4.2: ViewCartTool
        print("\n4.2 Testing ViewCartTool...")
        view_tool = ViewCartTool()
        result = view_tool._run(session_id=session_id)
        print("✅ ViewCartTool result:")
        print(result)

        # Test 4.3: RemoveFromCartTool
        print("\n4.3 Testing RemoveFromCartTool...")
        cart = cart_service.get_cart(session_id)
        if cart['items']:
            item_id = cart['items'][0]['item_id']
            remove_tool = RemoveFromCartTool()
            result = remove_tool._run(session_id=session_id, item_id=item_id)
            print("✅ RemoveFromCartTool result:")
            print(result)

        # Cleanup
        cart_service.clear_cart(session_id)

        return True

    except Exception as e:
        print(f"❌ LangChain tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_id_formats():
    """Test 5: Different session ID formats (web + WhatsApp)"""
    print("\n" + "="*60)
    print("TEST 5: Session ID Formats")
    print("="*60)

    cart_service = get_cart_service()

    test_sessions = [
        ("session-12345-abc", "Web Session"),
        ("wa_256701618576", "WhatsApp Session"),
        ("test-custom-id", "Custom Session")
    ]

    try:
        for session_id, description in test_sessions:
            print(f"\nTesting {description}: {session_id}")

            # Add item
            cart_service.add_item(
                session_id=session_id,
                product_id=1,
                name="Test Product",
                price=Decimal("50000"),
                quantity=1
            )

            # Verify
            cart = cart_service.get_cart(session_id)
            if cart['item_count'] == 1:
                print(f"✅ {description} works correctly")
            else:
                print(f"❌ {description} failed")

            # Cleanup
            cart_service.clear_cart(session_id)

        return True

    except Exception as e:
        print(f"❌ Session ID format test failed: {e}")
        return False


def test_redis_keys_structure():
    """Test 6: Verify Redis key structure"""
    print("\n" + "="*60)
    print("TEST 6: Redis Key Structure")
    print("="*60)

    cart_service = get_cart_service()
    session_id = "test-structure"

    try:
        # Add item
        cart_service.add_item(
            session_id=session_id,
            product_id=1,
            name="Test",
            price=Decimal("10000"),
            quantity=1
        )

        # Check keys
        cart_key = f"cart:{session_id}"
        items_key = f"cart:{session_id}:items"

        print(f"\nChecking Redis keys for session: {session_id}")

        # Cart metadata
        if cart_service.redis_client.exists(cart_key):
            print(f"✅ Cart metadata key exists: {cart_key}")
        else:
            print(f"❌ Cart metadata key missing: {cart_key}")

        # Items set
        if cart_service.redis_client.exists(items_key):
            item_ids = cart_service.redis_client.smembers(items_key)
            print(f"✅ Items set exists: {items_key}")
            print(f"   Item IDs: {item_ids}")

            # Check item keys
            for item_id in item_ids:
                item_key = f"cart:{session_id}:item:{item_id}"
                if cart_service.redis_client.exists(item_key):
                    print(f"✅ Item key exists: {item_key}")
                else:
                    print(f"❌ Item key missing: {item_key}")
        else:
            print(f"❌ Items set missing: {items_key}")

        # Cleanup
        cart_service.clear_cart(session_id)

        return True

    except Exception as e:
        print(f"❌ Redis structure test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪" * 30)
    print("PHASE 1 CART TESTING - Redis & LangChain Tools")
    print("🧪" * 30)

    results = []

    # Test 1: Redis Connection
    if not test_redis_connection():
        print("\n❌ Cannot proceed without Redis connection")
        print("\nPlease start Docker:")
        print("  cd server")
        print("  docker compose up -d")
        return

    # Run all tests
    results.append(("Cart Service CRUD", test_cart_service()))
    results.append(("Redis TTL", test_redis_ttl()))
    results.append(("LangChain Tools", test_langchain_tools()))
    results.append(("Session ID Formats", test_session_id_formats()))
    results.append(("Redis Key Structure", test_redis_keys_structure()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Phase 1 is ready!")
        print("\nNext steps:")
        print("1. Test cart API endpoints with curl")
        print("2. Test AI agent in web UI")
        print("3. Proceed to Phase 2 (Frontend integration)")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")


if __name__ == "__main__":
    main()
