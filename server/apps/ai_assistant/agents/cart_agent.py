"""
Cart Management Agent
Specialist for cart operations (add, remove, view, update).
Uses Claude Haiku for fast, simple cart operations.
"""

from typing import Dict, Optional, List
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

from .base_agent import BaseAgent, AgentContext, AgentResponse
from ..services.langchain_tools import (
    ViewCartTool,
    AddToCartTool,
    RemoveFromCartTool,
    UpdateCartQuantityTool,
)


class CartManagementAgent(BaseAgent):
    """
    Cart management specialist using Claude Haiku (fast, cheap).
    Handles simple CRUD operations on cart.
    """

    def __init__(self):
        """Initialize cart agent with Claude Haiku (fast and cheap for simple tasks)."""
        super().__init__(
            model_name="claude-3-5-haiku-20241022",
            temperature=0.3  # Lower temp for consistent cart operations
        )
        self.agent_executor = None

    @property
    def agent_name(self) -> str:
        return "cart"

    @property
    def agent_description(self) -> str:
        return "Specialist for cart operations: add items, remove items, view cart, update quantities"

    def get_system_prompt(self, context: AgentContext) -> str:
        """
        Focused system prompt for cart operations.
        Simple and concise for Haiku (~300 tokens).
        """
        cart_count = context.get_state('cart_items_count', 0)

        return f"""You are the Cart Management specialist for this e-commerce store.

CURRENT CART STATUS:
- Items in cart: {cart_count}

YOUR TOOLS:
- view_cart: Show what's in the cart
- add_to_cart: Add products to cart (requires session_id, product_id, quantity)
- remove_from_cart: Remove items from cart (requires session_id, product_id)
- update_cart_quantity: Change item quantity (requires session_id, product_id, new_quantity)

YOUR RESPONSIBILITIES:
✅ Add items to cart when user confirms purchase intent
✅ Remove items when user changes mind
✅ Update quantities when user wants more/less
✅ Show cart summary with totals
✅ Confirm actions with clear feedback

IMPORTANT NOTES:
- **ALWAYS use session_id from context** (it's in [Context: Session ID: ...])
- After ANY cart operation, show updated cart total
- Be clear about what was added/removed/updated
- Mention if product is out of stock or unavailable

HANDOFF CONDITIONS:
- User wants to find more products → Hand off to product_discovery
- User ready to checkout → Hand off to checkout
- Cart is empty and user wants checkout → Suggest finding products first

RESPONSE FORMAT:
After cart operations, always format like this:
✅ [Action completed] - [Product name]
💰 Price: [currency] [amount]
🛒 Cart total: [currency] [total] ([count] items)
[Ask: "Ready to checkout?" or "Anything else?"]

Remember: You're the cart specialist. Keep it simple, fast, and accurate."""

    def get_tools(self) -> List:
        """Get cart management tools."""
        return [
            ViewCartTool(),
            AddToCartTool(),
            RemoveFromCartTool(),
            UpdateCartQuantityTool(),
        ]

    def should_handoff(self, user_message: str, context: AgentContext) -> Optional[Dict]:
        """
        Check if should hand off to product discovery or checkout.
        """
        message_lower = user_message.lower()

        # Checkout triggers
        checkout_triggers = ['checkout', 'pay', 'complete order', 'proceed', 'finish order']
        if any(trigger in message_lower for trigger in checkout_triggers):
            cart_count = context.get_state('cart_items_count', 0)
            if cart_count > 0:
                return {
                    'agent': 'checkout',
                    'reason': 'User ready to checkout'
                }
            else:
                # Don't hand off - let agent suggest adding items first
                return None

        # Product discovery triggers
        product_triggers = ['show me', 'find', 'search', 'browse', 'look for', 'recommend']
        if any(trigger in message_lower for trigger in product_triggers):
            return {
                'agent': 'product_discovery',
                'reason': 'User wants to browse products'
            }

        return None

    def _generate_response(self, context: AgentContext) -> AgentResponse:
        """
        Generate response using cart tools.
        """
        # Initialize LLM and agent
        self._initialize_llm()

        if not self.agent_executor:
            self._initialize_agent()

        # Build input with context (includes session_id!)
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
            response_text = response_messages[-1].content if response_messages else 'I could not process that cart operation.'

            # Update cart count in state if tools were used
            tools_used = self._extract_tools_used(result)
            if any(tool in ['add_to_cart', 'remove_from_cart', 'update_cart_quantity'] for tool in tools_used):
                # Cart was modified - could refresh count here
                pass

            # Check if response suggests handoff
            handoff_info = self._check_response_for_handoff(response_text, context)

            return AgentResponse(
                content=response_text,
                handoff_to=handoff_info.get('agent') if handoff_info else None,
                handoff_reason=handoff_info.get('reason') if handoff_info else None,
                metadata={
                    'agent': self.agent_name,
                    'tools_used': tools_used,
                }
            )

        except Exception as e:
            return AgentResponse(
                content=f"I apologize, I encountered an error with the cart operation: {str(e)}. "
                       "Could you please try again?",
                metadata={
                    'agent': self.agent_name,
                    'error': str(e)
                }
            )

    def _initialize_agent(self):
        """Initialize LangGraph agent with cart tools."""
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

        # Check for checkout handoff signals
        checkout_signals = [
            'checkout specialist',
            'complete your order',
            'proceed to checkout',
            'ready to checkout'
        ]
        if any(signal in response_lower for signal in checkout_signals):
            return {'agent': 'checkout', 'reason': 'Agent suggested checkout'}

        # Check for product handoff signals
        product_signals = [
            'product specialist',
            'browse products',
            'find more',
            'product discovery'
        ]
        if any(signal in response_lower for signal in product_signals):
            return {'agent': 'product_discovery', 'reason': 'Agent suggested product browsing'}

        return None
