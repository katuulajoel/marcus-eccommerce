"""
LangChain Agent Service
Replaces the hardcoded llm_service with an intelligent agent that uses tools.
NO HARDCODED KEYWORDS - Agent learns from database through tools!
"""

import os
from typing import Dict, List
# LangChain 1.0+ imports - using LangGraph for agents
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .langchain_tools import get_all_tools
from .index_service import get_index_service


class AgentService:
    """
    Intelligent conversational agent for e-commerce assistance.
    Uses LangChain tools to dynamically discover and interact with products.
    """

    def __init__(self):
        self.llm = None
        self.agent_executor = None
        self._initialized = False

    def _initialize_agent(self):
        """Initialize the LangChain agent with tools (lazy initialization)"""
        if self._initialized:
            return

        # Use Claude for chat + Ollama for embeddings
        claude_api_key = os.getenv('CLAUDE_API_KEY')
        if not claude_api_key:
            raise ValueError("CLAUDE_API_KEY environment variable not set")

        print("🔧 Using Claude Sonnet 4 for chat")
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.7,
            api_key=claude_api_key,
            max_tokens=4096
        )

        # Get dynamic tools (powered by database!)
        tools = get_all_tools()

        # Create dynamic system prompt (no hardcoded domain knowledge!)
        from langchain_core.prompts import ChatPromptTemplate
        system_prompt = self._build_dynamic_system_prompt()

        # Create agent using LangGraph's create_react_agent (LangChain 1.0+ way)
        # Use prompt parameter instead of state_modifier
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ])

        self.agent_executor = create_react_agent(
            model=self.llm,
            tools=tools,
            prompt=prompt
        )

        self._initialized = True

    def _build_dynamic_system_prompt(self) -> str:
        """
        Build system prompt dynamically from database.
        NO HARDCODED CATEGORIES OR PRODUCTS!
        """
        # Get dynamic info from context builder
        from .context_builder import context_builder

        categories = context_builder.get_categories()
        category_names = [cat['name'] for cat in categories]

        # Build prompt with discovered information
        prompt = f"""You are an AI shopping assistant for Marcus Custom Bikes, an e-commerce platform.

AVAILABLE PRODUCT CATEGORIES (discovered from database):
{', '.join(category_names)}

YOUR CAPABILITIES:
You have access to tools that let you:
- Search for products using semantic search
- Find categories based on user needs
- Validate product configurations for compatibility
- Get part options and pricing
- Check inventory and stock status
- Calculate price ranges
- **ADD items to shopping cart** (NEW - You can take action!)
- **VIEW and MANAGE cart** (remove items, update quantities)

AUTONOMOUS SHOPPING ACTIONS - YOU CAN TAKE ACTION!:
✅ **You CAN add items to cart** - Don't just recommend, TAKE ACTION when user wants to buy!

**WHEN TO ADD TO CART (use add_to_cart tool):**
- User says "I want", "add to cart", "order", "buy", "I'll take it"
- User confirms after seeing product: "yes", "sure", "that one", "sounds good"
- User gives clear buying intent

**ASK FIRST if intent is unclear:**
- "Should I add this to your cart?"
- "Would you like me to add [product] for you?"

**AFTER ADDING TO CART, ALWAYS:**
1. Confirm what was added: "✅ Added 2x Balloon Bouquet"
2. Show price: "UGX 120,000 each = UGX 240,000"
3. Show cart total: "Cart total: UGX 375,000"
4. Ask: "Ready to checkout?"

**CART MANAGEMENT:**
- View cart → use view_cart tool when user asks "what's in my cart?"
- Remove items → use remove_from_cart when user says "remove [item]"
- Update quantity → use update_cart_quantity for "change to 3" or "I want 5"

IMPORTANT GUIDELINES:
1. **Use Tools Actively**: Don't guess - use your tools to get accurate, real-time information from the database
2. **Be Conversational**: Have natural conversations, ask clarifying questions when needed
3. **Product Recommendations**: Use search_products tool to find items matching user needs
4. **Configuration Help**: Use validate_configuration when discussing custom builds
5. **Pricing**: Use get_price_range and get_part_options for accurate pricing
6. **Stock**: Always mention stock status when recommending products
7. **No Hallucination**: Only recommend products that exist in search results
8. **Take Initiative**: When user clearly wants to buy, ADD TO CART proactively

CONVERSATION STYLE:
- Friendly and helpful, like a knowledgeable sales associate
- Ask follow-up questions to understand needs better
- Explain technical details in simple terms
- Proactively suggest relevant products
- Help users make informed decisions
- **BE PROACTIVE** - Add to cart when user shows buying intent!

WHEN USER ASKS ABOUT:
- Products → Use search_products tool
- Categories → Use search_categories or get_available_categories
- Customization → Use get_part_options and validate_configuration
- Pricing → Use get_price_range and search_products
- Compatibility → Use validate_configuration
- **Buying/Ordering** → Use add_to_cart tool (TAKE ACTION!)
- Cart status → Use view_cart tool
- Remove/Change items → Use remove_from_cart or update_cart_quantity
- **Checkout/Payment** → Use checkout tools (guide step-by-step!)

CHECKOUT FLOW - GUIDE USER STEP BY STEP (Phase 4):

**IMPORTANT: Order is created immediately after shipping selection!**
Users can pay now OR pay later from "My Orders" page.

**WHEN USER SAYS "checkout", "ready to pay", "complete order":**
1. Use `initiate_checkout` tool
2. Ask: "What's your delivery address?" (name, phone, street, city)

**WHEN USER PROVIDES ADDRESS:**
Example: "John Doe, +256701234567, Plot 123 Main St, Kampala"
1. Parse: recipient_name, phone_number, address_line1, city
2. Use `collect_shipping_address` tool with extracted info
3. Tool will show shipping options automatically
4. Ask: "Which delivery method do you prefer?"

**WHEN USER SELECTS SHIPPING:**
Examples: "standard delivery", "pickup", "express"
1. Map user response to method code:
   - "pickup"/"store pickup"/"collect" → pickup
   - "standard"/"normal"/"regular" → standard
   - "express"/"fast"/"next day" → express
2. Use `select_shipping_method` tool
3. **IMPORTANT:** This tool now CREATES THE ORDER automatically!
4. Tool shows:
   - Order number (e.g., "Order #4 Created!")
   - Order summary with total
   - Payment options
5. Tell user: "Your order is saved! You can pay now or pay later from My Orders."
6. Ask: "How would you like to pay? (Or you can pay later from My Orders)"

**WHEN USER SELECTS PAYMENT:**
1. Map payment method:
   - "card"/"credit card"/"stripe" → stripe
   - "mtn"/"mobile money"/"mtn money" → mtn_mobile_money
   - "airtel"/"airtel money" → airtel_money
   - "cash"/"cash on delivery"/"cod" → cash_on_delivery
2. Use `generate_payment_link` tool (order already exists!)
3. Share payment link/USSD code with user

**IF USER SAYS "pay later" or "I'll pay later":**
1. Confirm order number
2. Tell them: "✅ Order saved! You can pay anytime from the 'My Orders' page."
3. No need to call generate_payment_link

**PAYMENT METHOD INFO:**
- Card Payment (Stripe): Share clickable payment link
- MTN Mobile Money: Share USSD code *165*3# with steps
- Airtel Money: Share USSD code *185*9# with steps
- Cash on Delivery: Confirm order, no payment needed upfront

**ADDRESS FORMAT EXAMPLES:**
✅ Good: "John Doe, +256701234567, Plot 123 Main Street, Kampala"
✅ Good: "Jane Smith, +256700000000, Kira Road Apt 5, Kampala"
❌ Bad: "Plot 123" (missing name and phone)

**SHIPPING OPTIONS (auto-shown after address):**
- Store Pickup: FREE (Kampala/Entebbe only)
- Standard Delivery: UGX 15,000 (2-3 days, free on orders >500k)
- Express Delivery: UGX 30,000 (next day, Kampala/Entebbe only)

EXAMPLE FULL CHECKOUT FLOW:
User: "I want to checkout"
You: [Use initiate_checkout] "✅ Starting checkout! Cart: 2 items - UGX 240,000. What's your delivery address? Please provide: name, phone, street address, and city."

User: "John Doe, +256701234567, Plot 123 Main St, Kampala"
You: [Use collect_shipping_address] "✅ Address confirmed! Delivering to John Doe, Plot 123 Main St, Kampala. 🚚 Available delivery options: 1. 🏪 Store Pickup - FREE ... Which delivery method do you prefer?"

User: "standard delivery"
You: [Use select_shipping_method] "✅ Standard delivery selected! Order Summary: Subtotal UGX 240,000 + Shipping UGX 15,000 = Total UGX 255,000. How would you like to pay?"

User: "MTN mobile money"
You: [Use create_order] [Use generate_payment_link] "✅ Order #42 created! 📱 MTN Mobile Money Payment - Dial *165*3# and follow these steps: ..."

Remember: You're not just a recommendation engine - you're a complete shopping assistant who can guide users from browsing to payment!
"""

        return prompt

    def generate_response(
        self,
        user_message: str,
        context: Dict = None,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Generate AI response using the agent.
        Agent will decide which tools to use based on the query!

        Args:
            user_message: User's message
            context: Session context (current page, category, configuration, etc.)
            conversation_history: Previous messages in conversation

        Returns:
            Dict with 'content' (response text) and 'metadata' (tool calls, products, etc.)
        """
        # Initialize agent on first use
        self._initialize_agent()

        try:
            # Build input with context
            full_input = self._build_input_with_context(user_message, context)

            # Convert conversation history to LangChain format
            chat_history = self._format_conversation_history(conversation_history)

            # Run agent (LangGraph API uses messages)
            messages = chat_history + [HumanMessage(content=full_input)]
            result = self.agent_executor.invoke({"messages": messages})

            # Extract response (LangGraph returns messages)
            response_messages = result.get('messages', [])
            response_text = response_messages[-1].content if response_messages else ''

            # Build metadata
            metadata = {
                "tools_used": self._extract_tools_used(result),
                "agent_steps": len(result.get('intermediate_steps', [])),
            }

            return {
                "content": response_text,
                "metadata": metadata
            }

        except Exception as e:
            # Fallback response
            return {
                "content": f"I apologize, but I encountered an error: {str(e)}. Could you please rephrase your question?",
                "metadata": {"error": str(e)}
            }

    def _build_input_with_context(self, user_message: str, context: Dict = None) -> str:
        """
        Enhance user message with session context.
        Provides agent with situational awareness.
        """
        if not context:
            return user_message

        # Build context string
        context_parts = []

        # IMPORTANT: Include session_id for cart tools
        if context.get('session_id'):
            context_parts.append(f"Session ID: {context['session_id']}")

        if context.get('currentPage'):
            context_parts.append(f"User is on page: {context['currentPage']}")

        if context.get('categoryId'):
            from .context_builder import context_builder
            category_context = context_builder.build_category_context(int(context['categoryId']))
            if category_context:
                context_parts.append(f"Viewing category: {category_context.get('category_name')}")

        if context.get('productId'):
            context_parts.append(f"Looking at product ID: {context['productId']}")

        if context.get('configuration'):
            context_parts.append(f"Current configuration: {context['configuration']}")

        if context_parts:
            context_str = "\n".join(context_parts)
            return f"[Context: {context_str}]\n\nUser: {user_message}"

        return user_message

    def _format_conversation_history(self, history: List[Dict] = None) -> List:
        """Convert Django message history to LangChain format"""
        if not history:
            return []

        langchain_history = []
        for msg in history:
            role = msg.get('role')
            content = msg.get('content', '')

            if role == 'user':
                langchain_history.append(HumanMessage(content=content))
            elif role == 'assistant':
                langchain_history.append(AIMessage(content=content))
            elif role == 'system':
                langchain_history.append(SystemMessage(content=content))

        return langchain_history

    def _extract_tools_used(self, result: Dict) -> List[str]:
        """Extract which tools the agent used"""
        tools_used = []
        intermediate_steps = result.get('intermediate_steps', [])

        for step in intermediate_steps:
            if len(step) >= 1:
                action = step[0]
                if hasattr(action, 'tool'):
                    tools_used.append(action.tool)

        return list(set(tools_used))  # Deduplicate

    def ask_question(self, question: str) -> str:
        """
        Simple question-answering interface.
        Uses both tools and LlamaIndex knowledge base.
        """
        # Try agent first
        result = self.generate_response(question)

        if result['content']:
            return result['content']

        # Fallback to LlamaIndex direct query
        index_service = get_index_service()
        return index_service.ask_question(question)


# Global instance
_agent_service_instance = None


def get_agent_service() -> AgentService:
    """
    Get or create the global AgentService instance.
    """
    global _agent_service_instance

    if _agent_service_instance is None:
        _agent_service_instance = AgentService()

    return _agent_service_instance
