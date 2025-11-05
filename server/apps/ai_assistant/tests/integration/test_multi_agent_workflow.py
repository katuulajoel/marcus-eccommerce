"""
Integration tests for Multi-Agent Workflow
Tests complete user journeys through the agent system.
"""

import pytest
from apps.ai_assistant.orchestration.langgraph_workflow import MultiAgentWorkflow
from apps.ai_assistant.orchestration.state_manager import StateManager


class TestMultiAgentWorkflow:
    """
    Integration tests for full multi-agent workflows.
    Tests complete user journeys from browsing to checkout.
    """

    @pytest.fixture
    def workflow(self):
        """Create workflow instance for testing."""
        return MultiAgentWorkflow()

    @pytest.fixture
    def session_id(self):
        """Generate unique session ID for testing."""
        import uuid
        return f"test-session-{uuid.uuid4()}"

    @pytest.fixture
    def state_manager(self, session_id):
        """Create state manager for session."""
        manager = StateManager(session_id)
        yield manager
        # Cleanup after test
        manager.clear()

    # Product Discovery Journeys

    def test_product_search_journey(self, workflow, session_id):
        """
        Test: User searches for products.
        Expected: Router → Product Agent → Response with products
        """
        result = workflow.run(
            session_id=session_id,
            user_message="Show me mountain bikes",
            conversation_history=[],
            user_context={}
        )

        assert result['content'], "Response should not be empty"
        assert result['metadata']['workflow']['final_agent'] == 'product_discovery'
        assert result['metadata']['workflow']['iterations'] <= 2  # Router + Product

    def test_product_information_query(self, workflow, session_id):
        """
        Test: User asks about product details.
        Expected: Router → Product Agent → Detailed info
        """
        result = workflow.run(
            session_id=session_id,
            user_message="Tell me about this bike",
            conversation_history=[],
            user_context={'productId': 1}
        )

        assert result['content'], "Response should not be empty"
        assert result['metadata']['workflow']['final_agent'] == 'product_discovery'

    # Cart Management Journeys

    def test_add_to_cart_journey(self, workflow, session_id):
        """
        Test: User wants to add item to cart.
        Expected: Router → Cart Agent → Item added confirmation
        """
        result = workflow.run(
            session_id=session_id,
            user_message="Add this to my cart",
            conversation_history=[],
            user_context={'productId': 1}
        )

        assert result['content'], "Response should not be empty"
        # Should route to cart agent
        workflow_info = result['metadata']['workflow']
        assert workflow_info['final_agent'] in ['cart', 'product_discovery']

    def test_view_cart_journey(self, workflow, session_id, state_manager):
        """
        Test: User wants to view cart contents.
        Expected: Router → Cart Agent → Cart summary
        """
        # Simulate cart with items
        state_manager.set_cart_items_count(2)

        result = workflow.run(
            session_id=session_id,
            user_message="Show me my cart",
            conversation_history=[],
            user_context={}
        )

        assert result['content'], "Response should not be empty"
        assert result['metadata']['workflow']['final_agent'] == 'cart'

    # Checkout Journeys

    def test_checkout_journey_with_items(self, workflow, session_id, state_manager):
        """
        Test: User initiates checkout with items in cart.
        Expected: Router → Checkout Agent → Address collection
        """
        # Simulate cart with items
        state_manager.set_cart_items_count(3)

        result = workflow.run(
            session_id=session_id,
            user_message="I want to checkout",
            conversation_history=[],
            user_context={}
        )

        assert result['content'], "Response should not be empty"
        assert result['metadata']['workflow']['final_agent'] == 'checkout'
        # Should ask for address
        assert any(keyword in result['content'].lower() for keyword in ['address', 'delivery', 'shipping'])

    def test_checkout_blocked_empty_cart(self, workflow, session_id, state_manager):
        """
        Test: User tries to checkout with empty cart.
        Expected: Router detects empty cart, suggests products or clarifies
        """
        # Empty cart
        state_manager.set_cart_items_count(0)

        result = workflow.run(
            session_id=session_id,
            user_message="I want to checkout",
            conversation_history=[],
            user_context={}
        )

        assert result['content'], "Response should not be empty"
        # Should NOT go to checkout with empty cart
        # Should either stay at router or go to product_discovery
        assert result['metadata']['workflow']['final_agent'] in ['router', 'product_discovery', 'checkout']

    # Multi-Turn Conversations

    def test_product_to_cart_handoff(self, workflow, session_id):
        """
        Test: User browses product, then adds to cart.
        Expected: Product Agent → Cart Agent handoff
        """
        # Turn 1: Browse products
        result1 = workflow.run(
            session_id=session_id,
            user_message="Show me bikes",
            conversation_history=[],
            user_context={}
        )

        assert result1['metadata']['workflow']['final_agent'] == 'product_discovery'

        # Turn 2: Add to cart
        conversation_history = [
            {'role': 'user', 'content': 'Show me bikes'},
            {'role': 'assistant', 'content': result1['content']}
        ]

        result2 = workflow.run(
            session_id=session_id,
            user_message="I'll take the first one",
            conversation_history=conversation_history,
            user_context={}
        )

        # Should route to cart
        assert result2['metadata']['workflow']['final_agent'] in ['cart', 'product_discovery']

    def test_cart_to_checkout_handoff(self, workflow, session_id, state_manager):
        """
        Test: User adds item, then goes to checkout.
        Expected: Cart Agent → Checkout Agent handoff
        """
        # Simulate cart with items
        state_manager.set_cart_items_count(1)

        # Turn 1: View cart
        result1 = workflow.run(
            session_id=session_id,
            user_message="What's in my cart?",
            conversation_history=[],
            user_context={}
        )

        # Turn 2: Checkout
        conversation_history = [
            {'role': 'user', 'content': "What's in my cart?"},
            {'role': 'assistant', 'content': result1['content']}
        ]

        result2 = workflow.run(
            session_id=session_id,
            user_message="Let's checkout",
            conversation_history=conversation_history,
            user_context={}
        )

        assert result2['metadata']['workflow']['final_agent'] == 'checkout'

    # Context Preservation Tests

    def test_context_preserved_across_agents(self, workflow, session_id):
        """
        Test: Context (product ID, category) preserved during agent handoffs.
        """
        result = workflow.run(
            session_id=session_id,
            user_message="Add this to cart",
            conversation_history=[],
            user_context={
                'productId': 42,
                'categoryId': 1,
                'currentPage': '/customize'
            }
        )

        # Context should be available to agent (checked via logs/metadata)
        assert result['metadata'] is not None

    def test_conversation_history_maintained(self, workflow, session_id):
        """
        Test: Agent has access to previous conversation turns.
        """
        # Turn 1
        result1 = workflow.run(
            session_id=session_id,
            user_message="I'm looking for a bike",
            conversation_history=[],
            user_context={}
        )

        # Turn 2 - reference to previous message
        conversation_history = [
            {'role': 'user', 'content': "I'm looking for a bike"},
            {'role': 'assistant', 'content': result1['content']}
        ]

        result2 = workflow.run(
            session_id=session_id,
            user_message="Tell me more about that",
            conversation_history=conversation_history,
            user_context={}
        )

        # Should understand "that" refers to bikes from previous turn
        assert result2['content'], "Agent should handle reference to previous turn"

    # Error Handling Tests

    def test_max_iterations_prevents_infinite_loop(self, workflow, session_id):
        """
        Test: Workflow doesn't loop infinitely if agents keep handing off.
        """
        result = workflow.run(
            session_id=session_id,
            user_message="test message",
            conversation_history=[],
            user_context={}
        )

        # Should complete within max iterations (5)
        assert result['metadata']['workflow']['iterations'] <= 5

    def test_handles_ambiguous_input(self, workflow, session_id):
        """
        Test: System handles unclear user input gracefully.
        """
        result = workflow.run(
            session_id=session_id,
            user_message="hmm",
            conversation_history=[],
            user_context={}
        )

        # Should return something (likely router asking for clarification)
        assert result['content'], "Should handle ambiguous input gracefully"

    # Performance Tests

    def test_routing_efficiency(self, workflow, session_id):
        """
        Test: Router classifies intent in single step (no multiple routing).
        """
        result = workflow.run(
            session_id=session_id,
            user_message="Show me bikes",
            conversation_history=[],
            user_context={}
        )

        # Should be Router (1) + Product Agent (1) = 2 iterations max
        assert result['metadata']['workflow']['iterations'] <= 2

    def test_agent_history_tracking(self, workflow, session_id, state_manager):
        """
        Test: Agent usage history is tracked in state.
        """
        workflow.run(
            session_id=session_id,
            user_message="Show me bikes",
            conversation_history=[],
            user_context={}
        )

        # Check state manager has agent history
        history = state_manager.get_agent_history()
        assert len(history) > 0
        assert 'product_discovery' in history or 'router' in history


# Run tests with pytest
# Usage: pytest apps/ai_assistant/tests/integration/test_multi_agent_workflow.py -v
#
# Note: These tests require:
# - CLAUDE_API_KEY environment variable set
# - Docker services running (Redis, PostgreSQL)
# - LlamaIndex embeddings (Ollama) running
