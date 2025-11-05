"""
Product Discovery Agent
Expert in product search, recommendations, and product information.
Uses Claude Sonnet + LlamaIndex RAG for intelligent product discovery.
"""

from typing import Dict, Optional, List
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

from .base_agent import BaseAgent, AgentContext, AgentResponse
from ..services.index_service import get_index_service
from ..services.langchain_tools import (
    SearchProductsTool,
    SearchCategoriesTool,
    GetAvailableCategoriesTool,
    GetPartOptionsTool,
    ValidateConfigurationTool,
    GetPriceRangeTool,
)


class ProductDiscoveryAgent(BaseAgent):
    """
    Product discovery specialist using Claude Sonnet + RAG.
    Handles product search, recommendations, information queries.
    """

    def __init__(self):
        """Initialize product agent with Claude Sonnet (powerful reasoning)."""
        super().__init__(
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.7
        )
        self.agent_executor = None

    @property
    def agent_name(self) -> str:
        return "product_discovery"

    @property
    def agent_description(self) -> str:
        return "Expert in finding products, making recommendations, and answering product questions using semantic search and knowledge base"

    def get_system_prompt(self, context: AgentContext) -> str:
        """
        Focused system prompt for product discovery.
        Much shorter than the monolithic version (~400 tokens vs 2,500).
        """
        from ..services.context_builder import context_builder

        # Get categories dynamically
        categories = context_builder.get_categories()
        category_names = [cat['name'] for cat in categories]

        return f"""You are a Product Discovery specialist for an e-commerce store.

AVAILABLE CATEGORIES:
{', '.join(category_names)}

YOUR TOOLS (ALWAYS USE THESE - DO NOT MAKE UP INFORMATION):
- search_products: Search for products using semantic search (ALWAYS use this for product queries)
- search_categories: Find relevant categories
- get_part_options: Get customization/part details
- validate_configuration: Validate product configurations
- get_price_range: Calculate price ranges

CRITICAL INSTRUCTIONS:
1. **ALWAYS use search_products tool for ANY product query** - Never mention specific product names or categories without searching first
2. **NEVER assume what products exist** - Let the search results tell you what's available
3. **Base ALL recommendations on search results** - Don't use examples from this prompt
4. Ask clarifying questions when needed (budget, preferences, occasion, recipient)
5. Always mention stock status and pricing from tool results
6. Be friendly and helpful, adapting your expertise to whatever products are found

HANDOFF CONDITIONS:
- User wants to ADD ITEM to cart → Hand off to cart agent
- User wants to VIEW/MANAGE cart → Hand off to cart agent
- User wants to CHECKOUT → Hand off to checkout agent

WORKFLOW:
1. User asks about products → IMMEDIATELY use search_products tool with their query
2. Review search results → Recommend based on ACTUAL products found
3. User wants more details → Use search_products again for that specific product
4. User wants to buy → Hand off to cart agent

EXAMPLE FLOW:
User: "I want a gift for my girlfriend"
You: [IMMEDIATELY use search_products with query="gift girlfriend anniversary romantic"]
[Review results → See what products actually exist]
"I found some great gift options for your girlfriend:
1. [Product Name from results] - [Price from results]
2. [Product Name from results] - [Price from results]
What's your budget, and does she have any specific interests?"

Remember: You are a product discovery expert. ALWAYS use tools to find real products. Never invent product names or assume what's in the catalog."""

    def get_tools(self) -> List:
        """Get product discovery tools."""
        return [
            SearchProductsTool(),
            SearchCategoriesTool(),
            GetAvailableCategoriesTool(),
            GetPartOptionsTool(),
            ValidateConfigurationTool(),
            GetPriceRangeTool(),
        ]

    def should_handoff(self, user_message: str, context: AgentContext) -> Optional[Dict]:
        """
        Check if should hand off to cart or checkout.
        """
        message_lower = user_message.lower()

        # Explicit handoff triggers
        cart_triggers = ['add to cart', 'add it', 'buy this', 'purchase', 'order this', 'take it']
        if any(trigger in message_lower for trigger in cart_triggers):
            return {
                'agent': 'cart',
                'reason': 'User wants to add item to cart'
            }

        checkout_triggers = ['checkout', 'pay', 'complete order', 'finish']
        if any(trigger in message_lower for trigger in checkout_triggers):
            cart_count = context.get_state('cart_items_count', 0)
            if cart_count > 0:
                return {
                    'agent': 'checkout',
                    'reason': 'User ready to checkout'
                }

        view_cart_triggers = ['show cart', 'view cart', 'what\'s in cart', 'my cart']
        if any(trigger in message_lower for trigger in view_cart_triggers):
            return {
                'agent': 'cart',
                'reason': 'User wants to view cart'
            }

        return None

    def _generate_response(self, context: AgentContext) -> AgentResponse:
        """
        Generate response using tools and RAG.
        """
        # Initialize LLM and agent
        self._initialize_llm()

        if not self.agent_executor:
            self._initialize_agent()

        # Build input with context
        full_input = self._build_input_with_context(context.user_message, context)

        # Convert conversation history
        chat_history = self._format_conversation_history(context.conversation_history)

        try:
            # Get system prompt
            system_prompt = self.get_system_prompt(context)

            # Run agent with tools - add system message at the start
            messages = [SystemMessage(content=system_prompt)] + chat_history + [HumanMessage(content=full_input)]
            result = self.agent_executor.invoke({"messages": messages})

            # Extract response
            response_messages = result.get('messages', [])
            response_text = response_messages[-1].content if response_messages else 'I apologize, I could not process that request.'

            # Check if response suggests handoff
            handoff_info = self._check_response_for_handoff(response_text, context)

            return AgentResponse(
                content=response_text,
                handoff_to=handoff_info.get('agent') if handoff_info else None,
                handoff_reason=handoff_info.get('reason') if handoff_info else None,
                metadata={
                    'agent': self.agent_name,
                    'tools_used': self._extract_tools_used(result),
                }
            )

        except Exception as e:
            # Fallback to LlamaIndex RAG
            return self._fallback_to_rag(context, error=str(e))

    def _initialize_agent(self):
        """Initialize LangGraph agent with tools."""
        tools = self.get_tools()

        # Create agent without prompt - we'll add system message in _generate_response
        self.agent_executor = create_react_agent(
            model=self.llm,
            tools=tools
        )

    def _extract_tools_used(self, result: Dict) -> List[str]:
        """Extract which tools were called."""
        tools_used = []
        for message in result.get('messages', []):
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    tools_used.append(tool_call.get('name', 'unknown'))
        return list(set(tools_used))

    def _check_response_for_handoff(self, response_text: str, context: AgentContext) -> Optional[Dict]:
        """
        Check if agent's response indicates it wants to hand off.
        """
        response_lower = response_text.lower()

        # Check for cart handoff signals
        cart_signals = [
            'connect you with our cart specialist',
            'add it to your cart',
            'cart specialist',
            'add to cart for you'
        ]
        if any(signal in response_lower for signal in cart_signals):
            return {'agent': 'cart', 'reason': 'Agent suggested cart action'}

        # Check for checkout handoff signals
        checkout_signals = [
            'proceed to checkout',
            'checkout specialist',
            'ready to complete your order'
        ]
        if any(signal in response_lower for signal in checkout_signals):
            return {'agent': 'checkout', 'reason': 'Agent suggested checkout'}

        return None

    def _fallback_to_rag(self, context: AgentContext, error: str = None) -> AgentResponse:
        """
        Fallback to direct LlamaIndex RAG query if agent fails.
        """
        try:
            index_service = get_index_service()
            rag_response = index_service.ask_question(context.user_message)

            return AgentResponse(
                content=rag_response,
                metadata={
                    'agent': self.agent_name,
                    'fallback': 'RAG',
                    'error': error
                }
            )
        except Exception as rag_error:
            return AgentResponse(
                content="I apologize, but I'm having trouble accessing product information right now. "
                       "Could you please try rephrasing your question?",
                metadata={
                    'agent': self.agent_name,
                    'error': error,
                    'rag_error': str(rag_error)
                }
            )
