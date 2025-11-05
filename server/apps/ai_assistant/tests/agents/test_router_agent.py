"""
Unit tests for RouterAgent
Tests intent classification accuracy (target: 95%+)
"""

import pytest
from apps.ai_assistant.agents.router_agent import RouterAgent


class TestRouterAgent:
    """Test suite for RouterAgent intent classification."""

    @pytest.fixture
    def router(self):
        """Create RouterAgent instance for testing."""
        return RouterAgent()

    # Product Discovery Intent Tests

    def test_product_search_queries(self, router):
        """Test product search intent classification."""
        queries = [
            "Show me mountain bikes",
            "I'm looking for a road bike",
            "Find me bikes under $1000",
            "What bikes do you have?",
            "Do you sell surfboards?",
            "Recommend a bike for beginners",
            "Which bike is best for trails?",
        ]

        for query in queries:
            result = router.classify_intent(query)
            assert result['agent'] == 'product_discovery', \
                f"Failed for query: '{query}' - got {result['agent']}"
            assert result['confidence'] > 0.7, \
                f"Low confidence for query: '{query}' - got {result['confidence']}"

    def test_product_information_queries(self, router):
        """Test product information intent classification."""
        queries = [
            "Tell me about this bike",
            "What are the specifications?",
            "How much does it cost?",
            "Is this in stock?",
            "What colors are available?",
        ]

        for query in queries:
            result = router.classify_intent(query)
            assert result['agent'] == 'product_discovery', \
                f"Failed for query: '{query}' - got {result['agent']}"

    def test_general_queries(self, router):
        """Test general queries route to product discovery."""
        queries = [
            "Hello",
            "Hi there",
            "What can you help me with?",
            "I need help",
            "Thanks",
        ]

        for query in queries:
            result = router.classify_intent(query)
            assert result['agent'] == 'product_discovery', \
                f"Failed for query: '{query}' - got {result['agent']}"

    # Cart Intent Tests

    def test_add_to_cart_intents(self, router):
        """Test add to cart intent classification."""
        queries = [
            "Add this to my cart",
            "I want to buy this",
            "Add it to cart",
            "I'll take it",
            "Put this in my cart",
            "Order this bike",
            "Purchase this",
        ]

        for query in queries:
            result = router.classify_intent(query)
            assert result['agent'] == 'cart', \
                f"Failed for query: '{query}' - got {result['agent']}"
            assert result['confidence'] > 0.7, \
                f"Low confidence for query: '{query}' - got {result['confidence']}"

    def test_view_cart_intents(self, router):
        """Test view cart intent classification."""
        queries = [
            "Show me my cart",
            "What's in my cart?",
            "View cart",
            "Check my cart",
            "Cart status",
        ]

        for query in queries:
            result = router.classify_intent(query)
            assert result['agent'] == 'cart', \
                f"Failed for query: '{query}' - got {result['agent']}"

    def test_remove_from_cart_intents(self, router):
        """Test remove from cart intent classification."""
        queries = [
            "Remove this from cart",
            "Delete item from cart",
            "Take this out of my cart",
            "Remove the bike",
        ]

        for query in queries:
            result = router.classify_intent(query)
            assert result['agent'] == 'cart', \
                f"Failed for query: '{query}' - got {result['agent']}"

    # Checkout Intent Tests

    def test_checkout_initiation_intents(self, router):
        """Test checkout initiation intent classification."""
        queries = [
            "I want to checkout",
            "Ready to checkout",
            "Let's checkout",
            "Proceed to checkout",
            "Complete my order",
            "Finalize purchase",
        ]

        for query in queries:
            result = router.classify_intent(query)
            assert result['agent'] == 'checkout', \
                f"Failed for query: '{query}' - got {result['agent']}"
            assert result['confidence'] > 0.8, \
                f"Low confidence for query: '{query}' - got {result['confidence']}"

    def test_payment_intents(self, router):
        """Test payment intent classification."""
        queries = [
            "I want to pay",
            "How do I pay?",
            "Payment options",
            "Pay with card",
            "Mobile money payment",
        ]

        for query in queries:
            result = router.classify_intent(query)
            assert result['agent'] == 'checkout', \
                f"Failed for query: '{query}' - got {result['agent']}"

    def test_shipping_intents(self, router):
        """Test shipping/address intent classification."""
        queries = [
            "What's the shipping cost?",
            "Delivery options",
            "My address is...",
            "I want express delivery",
            "Store pickup",
        ]

        for query in queries:
            result = router.classify_intent(query)
            assert result['agent'] == 'checkout', \
                f"Failed for query: '{query}' - got {result['agent']}"

    # Context-Aware Tests

    def test_checkout_blocked_when_cart_empty(self, router):
        """Test that checkout is not suggested when cart is empty."""
        result = router.classify_intent(
            "I want to checkout",
            session_context={'cart_items_count': 0}
        )

        # Should either clarify or suggest product discovery
        assert result['needs_clarification'] or result['agent'] == 'product_discovery', \
            f"Should not route to checkout with empty cart - got {result['agent']}"

    def test_high_confidence_routing(self, router):
        """Test that clear intents have high confidence."""
        high_confidence_queries = [
            ("Show me mountain bikes", "product_discovery"),
            ("Add to cart", "cart"),
            ("Checkout", "checkout"),
        ]

        for query, expected_agent in high_confidence_queries:
            result = router.classify_intent(query)
            assert result['confidence'] >= 0.8, \
                f"Expected high confidence for '{query}' - got {result['confidence']}"
            assert result['agent'] == expected_agent, \
                f"Expected {expected_agent} for '{query}' - got {result['agent']}"

    def test_ambiguous_queries_handled(self, router):
        """Test that ambiguous queries are handled appropriately."""
        ambiguous_queries = [
            "Help",
            "What?",
            "Hmm",
            "Not sure",
        ]

        for query in ambiguous_queries:
            result = router.classify_intent(query)
            # Either low confidence or needs clarification
            assert result['confidence'] < 0.8 or result['needs_clarification'], \
                f"Ambiguous query '{query}' should have low confidence or need clarification"

    # Edge Cases

    def test_mixed_intent_queries(self, router):
        """Test queries with mixed intents."""
        # These should prioritize the strongest intent
        queries = [
            ("Show me bikes and add one to cart", "product_discovery"),  # Discovery first
            ("What's in my cart and checkout", "cart"),  # Cart before checkout
        ]

        for query, expected_agent in queries:
            result = router.classify_intent(query)
            assert result['agent'] == expected_agent, \
                f"Failed for mixed intent query: '{query}' - got {result['agent']}"

    def test_typos_and_variations(self, router):
        """Test that router handles typos and variations."""
        queries = [
            ("shwo me bikes", "product_discovery"),  # Typo in 'show'
            ("add too cart", "cart"),  # Typo in 'to'
            ("chekout", "checkout"),  # Typo in 'checkout'
        ]

        for query, expected_agent in queries:
            result = router.classify_intent(query)
            # Should still route correctly despite typos
            assert result['agent'] == expected_agent, \
                f"Failed to handle typo in: '{query}' - got {result['agent']}"

    # Accuracy Measurement

    def test_overall_routing_accuracy(self, router):
        """
        Test overall routing accuracy across all intents.
        Target: 95%+ accuracy
        """
        test_cases = [
            # Product Discovery (25 cases)
            ("Show me mountain bikes", "product_discovery"),
            ("Looking for a bike", "product_discovery"),
            ("What bikes do you have?", "product_discovery"),
            ("Find road bikes", "product_discovery"),
            ("Recommend a bike", "product_discovery"),
            ("Tell me about this bike", "product_discovery"),
            ("What's the price?", "product_discovery"),
            ("Is this in stock?", "product_discovery"),
            ("What colors available?", "product_discovery"),
            ("Hello", "product_discovery"),
            ("Hi there", "product_discovery"),
            ("I need help", "product_discovery"),
            ("Surfboards?", "product_discovery"),
            ("Which bike is best?", "product_discovery"),
            ("Bike for beginners", "product_discovery"),
            ("Mountain bike specs", "product_discovery"),
            ("Compare bikes", "product_discovery"),
            ("Best bike for trails", "product_discovery"),
            ("Show all products", "product_discovery"),
            ("What do you sell?", "product_discovery"),
            ("Product categories", "product_discovery"),
            ("Bike options", "product_discovery"),
            ("Tell me more", "product_discovery"),
            ("Features of this bike", "product_discovery"),
            ("Reviews", "product_discovery"),

            # Cart (15 cases)
            ("Add to cart", "cart"),
            ("I want to buy this", "cart"),
            ("Add this", "cart"),
            ("I'll take it", "cart"),
            ("Purchase this", "cart"),
            ("Order this bike", "cart"),
            ("Show my cart", "cart"),
            ("What's in my cart?", "cart"),
            ("View cart", "cart"),
            ("Check cart", "cart"),
            ("Remove from cart", "cart"),
            ("Delete item", "cart"),
            ("Update quantity", "cart"),
            ("Change to 2", "cart"),
            ("Empty cart", "cart"),

            # Checkout (10 cases)
            ("Checkout", "checkout"),
            ("I want to checkout", "checkout"),
            ("Complete order", "checkout"),
            ("Proceed to checkout", "checkout"),
            ("I want to pay", "checkout"),
            ("Payment", "checkout"),
            ("Shipping options", "checkout"),
            ("Delivery cost", "checkout"),
            ("My address is...", "checkout"),
            ("Express delivery", "checkout"),
        ]

        correct = 0
        total = len(test_cases)
        failures = []

        for query, expected_agent in test_cases:
            result = router.classify_intent(query)
            if result['agent'] == expected_agent:
                correct += 1
            else:
                failures.append({
                    'query': query,
                    'expected': expected_agent,
                    'got': result['agent'],
                    'confidence': result['confidence']
                })

        accuracy = (correct / total) * 100

        # Print failures for debugging
        if failures:
            print(f"\n❌ Routing failures ({len(failures)}/{total}):")
            for failure in failures:
                print(f"  - '{failure['query']}'")
                print(f"    Expected: {failure['expected']}, Got: {failure['got']} "
                      f"(confidence: {failure['confidence']:.2f})")

        assert accuracy >= 95.0, \
            f"Routing accuracy {accuracy:.1f}% is below target 95%. " \
            f"Correct: {correct}/{total}. See failures above."

        print(f"\n✅ Routing accuracy: {accuracy:.1f}% ({correct}/{total})")


# Run tests with pytest
# Usage: pytest apps/ai_assistant/tests/agents/test_router_agent.py -v
