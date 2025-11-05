"""
Checkout & Payment Agent
Expert in guiding users through checkout flow and payment.
Uses Claude Sonnet for complex multi-step checkout process.
"""

from typing import Dict, Optional, List
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

from .base_agent import BaseAgent, AgentContext, AgentResponse
from ..services.langchain_tools import (
    InitiateCheckoutTool,
    CollectShippingAddressTool,
    SelectShippingMethodTool,
    GeneratePaymentLinkTool,
)


class CheckoutPaymentAgent(BaseAgent):
    """
    Checkout & payment specialist using Claude Sonnet.
    Guides users through multi-step checkout flow with proper validation.
    """

    def __init__(self):
        """Initialize checkout agent with Claude Sonnet (complex reasoning for checkout flow)."""
        super().__init__(
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.5  # Moderate temp for guided but natural checkout
        )
        self.agent_executor = None

    @property
    def agent_name(self) -> str:
        return "checkout"

    @property
    def agent_description(self) -> str:
        return "Expert in checkout flow: collecting shipping address, selecting shipping method, and payment processing"

    def get_system_prompt(self, context: AgentContext) -> str:
        """
        System prompt for checkout flow.
        Detailed but focused on checkout (~600 tokens).
        """
        checkout_state = context.get_state('checkout', {})
        checkout_status = checkout_state.get('status', 'not_started')
        has_address = bool(checkout_state.get('shipping_address'))

        return f"""You are the Checkout & Payment specialist for this e-commerce store.

CURRENT CHECKOUT STATUS: {checkout_status}
Address collected: {has_address}

YOUR TOOLS:
1. initiate_checkout - Start checkout process, show cart summary
2. collect_shipping_address - Save shipping address (name, phone, street, city)
3. select_shipping_method - Choose shipping option AND CREATE ORDER
4. generate_payment_link - Generate payment link/instructions

CHECKOUT FLOW (IMPORTANT - Follow this sequence):

**STEP 1: Initiate Checkout**
- Use initiate_checkout tool
- Tool shows cart summary and total
- Ask: "What's your delivery address?"

**STEP 2: Collect Address**
User provides address in format: "Name, Phone, Street, City"
- Parse: recipient_name, phone_number, address_line1, city
- Use collect_shipping_address tool
- Tool automatically shows shipping options
- Ask: "Which delivery method do you prefer?"

**STEP 3: Select Shipping (ORDER CREATION HAPPENS HERE!)**
User selects delivery method
- Map user response to available shipping options
- Use select_shipping_method tool
- **IMPORTANT:** Tool creates order automatically!
- Tool returns order number + payment options
- Tell user: "✅ Order #X created! You can pay now or later."
- Ask: "How would you like to pay?"

**STEP 4: Payment (Optional - User can skip)**
User selects payment method or says "pay later"
- If "pay later" → Confirm order saved, no payment link needed
- Otherwise, use generate_payment_link tool
- Share payment link/instructions based on payment method

**VALIDATION RULES:**
❌ Can't collect address before initiating checkout
❌ Can't select shipping before collecting address
❌ Can't generate payment before selecting shipping (order must exist)
❌ Address must have: name, phone, street, city

**ERROR HANDLING:**
- If tool fails, explain what's missing
- Don't repeat failed actions - ask for missing info
- If validation fails, tell user exactly what's needed
- Keep track of checkout state

**HANDOFF CONDITIONS:**
- User wants to modify cart → Hand off to cart agent
- User wants to add more items → Hand off to product_discovery

Remember: Guide users step-by-step through checkout. Be patient, validate each step, and confirm order creation clearly."""

    def get_tools(self) -> List:
        """Get checkout tools."""
        return [
            InitiateCheckoutTool(),
            CollectShippingAddressTool(),
            SelectShippingMethodTool(),
            GeneratePaymentLinkTool(),
        ]

    def should_handoff(self, user_message: str, context: AgentContext) -> Optional[Dict]:
        """
        Check if should hand off to cart or product discovery.
        """
        message_lower = user_message.lower()

        # Cart modification triggers
        cart_triggers = ['modify cart', 'change cart', 'remove from cart', 'add to cart', 'view cart']
        if any(trigger in message_lower for trigger in cart_triggers):
            return {
                'agent': 'cart',
                'reason': 'User wants to modify cart during checkout'
            }

        # Product browsing triggers
        product_triggers = ['add more items', 'find more', 'browse', 'continue shopping']
        if any(trigger in message_lower for trigger in product_triggers):
            return {
                'agent': 'product_discovery',
                'reason': 'User wants to continue shopping'
            }

        return None

    def _generate_response(self, context: AgentContext) -> AgentResponse:
        """
        Generate response using checkout tools.
        """
        # Initialize LLM and agent
        self._initialize_llm()

        if not self.agent_executor:
            self._initialize_agent()

        # Build input with context (includes session_id and checkout state!)
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
            response_text = response_messages[-1].content if response_messages else 'I could not process that checkout step.'

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
            return AgentResponse(
                content=f"I apologize, I encountered an error during checkout: {str(e)}. "
                       "Let's try again. Where were we in the checkout process?",
                metadata={
                    'agent': self.agent_name,
                    'error': str(e)
                }
            )

    def _initialize_agent(self):
        """Initialize LangGraph agent with checkout tools."""
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
            'cart specialist',
            'modify your cart',
            'cart agent'
        ]
        if any(signal in response_lower for signal in cart_signals):
            return {'agent': 'cart', 'reason': 'Agent suggested cart modification'}

        # Check for product handoff signals
        product_signals = [
            'product specialist',
            'continue shopping',
            'browse more'
        ]
        if any(signal in response_lower for signal in product_signals):
            return {'agent': 'product_discovery', 'reason': 'Agent suggested product browsing'}

        return None
