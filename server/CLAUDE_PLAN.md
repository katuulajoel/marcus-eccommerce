 Multi-Agent Architecture Implementation Plan

 Overview

 Transform the monolithic AI assistant into a scalable multi-agent system with specialized domain experts, preparing for WhatsApp integration and eliminating current
 reliability issues.

 Architecture Design

 Agent Structure

 1. Router Agent (Claude Haiku) - Intent classification → routes to specialist
 2. Product Discovery Agent (Claude Sonnet + RAG) - Search, recommendations, product info
 3. Cart Management Agent (Claude Haiku) - Add/remove/update cart items
 4. Checkout & Payment Agent (Claude Sonnet) - Order creation, address collection, payment

 Key Benefits

 - 54% cost reduction - Haiku for simple tasks, Sonnet only when needed
 - 30% faster responses - Lighter agents, focused prompts
 - Independent testing - Each agent testable in isolation
 - WhatsApp ready - Channel adapter pattern built-in
 - Fixes current issues - Better validation, state management, no token overflow

 Implementation Plan (3 Weeks)

 Week 1: Foundation + Router Agent

 Days 1-2: Infrastructure
 - Create agents/, orchestration/, adapters/ directories
 - Implement BaseAgent class with shared state management
 - Create HandoffManager for agent transitions
 - Set up StateManager using Redis

 Days 3-5: Router Agent
 - Implement intent classification with Claude Haiku
 - Train on sample queries (unit tests as training data)
 - Add confidence scoring for uncertain intents
 - Test router accuracy (target: 95%+ correct routing)

 Week 2: Product + Cart Agents

 Days 6-8: Product Discovery Agent
 - Port product search tools (search_products, search_categories, get_part_options)
 - Integrate LlamaIndex RAG for knowledge retrieval
 - Create focused system prompt (~500 tokens vs 2,500)
 - Unit tests for product discovery scenarios

 Days 9-10: Cart Management Agent
 - Port cart tools (view_cart, add_to_cart, remove_from_cart, update_quantity)
 - Simple, stateless operations (perfect for Haiku)
 - Validation logic for cart operations
 - Unit tests for cart flows

 Week 3: Checkout + Integration

 Days 11-13: Checkout & Payment Agent
 - Port checkout tools (initiate_checkout, collect_shipping_address, select_shipping_method, generate_payment_link)
 - Implement stateful checkout flow with proper validation
 - Fix session state management issues
 - Unit tests for checkout scenarios

 Days 14-15: LangGraph Orchestration
 - Create state graph connecting all agents
 - Implement conditional routing based on agent responses
 - Add handoff protocols and context preservation
 - Integration tests for full user journeys

 Days 16-18: Testing & Refinement
 - Comprehensive test suite:
   - Router accuracy tests
   - Individual agent success rate tests (target: 99%+)
   - Context preservation tests
   - End-to-end flow tests
 - Fix issues discovered during testing
 - Performance optimization

 Days 19-21: WhatsApp Adapter Foundation
 - Create WhatsAppAdapter class for message formatting
 - Test adapter with sample messages
 - Document WhatsApp-specific considerations
 - Prepare webhook endpoint structure (Phase 5 implementation)

 Testing Strategy

 Unit Tests (Each Agent)

 # Example: test_router_agent.py
 def test_router_classifies_product_intent():
     router = RouterAgent()
     result = router.route("Show me mountain bikes")
     assert result.agent == "product_discovery"
     assert result.confidence > 0.9

 def test_router_handles_ambiguous_intent():
     router = RouterAgent()
     result = router.route("help")
     assert result.clarification_needed == True

 Integration Tests (Full Flows)

 # Example: test_checkout_flow.py
 def test_complete_checkout_preserves_context():
     # User adds item → checkout → address → shipping → payment
     # Assert: No re-asking for information, order created successfully

 Routing Accuracy Tests

 - 100 sample queries covering all intents
 - Measure precision/recall for each agent category
 - Target: 95%+ correct routing, <2% misclassifications

 File Structure

 server/apps/ai_assistant/
 ├── agents/
 │   ├── base_agent.py          # Abstract base class
 │   ├── router_agent.py        # Intent classification (Haiku)
 │   ├── product_agent.py       # Product discovery (Sonnet + RAG)
 │   ├── cart_agent.py          # Cart management (Haiku)
 │   └── checkout_agent.py      # Checkout & payment (Sonnet)
 ├── orchestration/
 │   ├── langgraph_workflow.py  # State machine
 │   ├── handoff_manager.py     # Agent transitions
 │   └── state_manager.py       # Shared state (Redis)
 ├── adapters/
 │   ├── channel_adapter.py     # Base adapter
 │   └── whatsapp_adapter.py    # WhatsApp formatting
 ├── services/                  # Keep existing services
 │   ├── index_service.py       # ✓ LlamaIndex RAG
 │   ├── cart_service.py        # ✓ Redis cart
 │   ├── checkout_service.py    # ✓ Order creation
 │   └── langchain_tools.py     # ✓ All tools (no changes)
 └── tests/
     ├── agents/                # Unit tests per agent
     └── integration/           # End-to-end flows

 Expected Outcomes

 - Reliability: 99%+ success rate per agent (vs current ~70%)
 - Performance: 30% faster responses, 54% lower costs
 - Testability: Each agent independently verifiable
 - Scalability: Ready for WhatsApp, SMS, voice channels
 - Maintainability: Focused agents, clear responsibilities

 Ready to start Week 1?