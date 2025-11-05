"""
Router Agent
Fast intent classification using Claude Haiku.
Routes user messages to the appropriate specialist agent.
"""

import json
import re
from typing import Dict, Optional
from langchain_core.messages import HumanMessage, SystemMessage

from .base_agent import BaseAgent, AgentContext, AgentResponse


class RouterAgent(BaseAgent):
    """
    Router agent that classifies user intent and routes to specialists.
    Uses Claude Haiku for fast, cheap intent classification.
    """

    def __init__(self):
        """Initialize router with Claude Haiku (fast and cheap)."""
        super().__init__(
            model_name="claude-3-5-haiku-20241022",
            temperature=0.3  # Lower temperature for consistent routing
        )

    @property
    def agent_name(self) -> str:
        return "router"

    @property
    def agent_description(self) -> str:
        return "Routes user messages to appropriate specialist agents (product discovery, cart, checkout)"

    def get_system_prompt(self, context: AgentContext) -> str:
        """
        System prompt for intent classification.
        Kept very concise for fast routing with Haiku.
        """
        # Get current state for context
        cart_count = context.get_state('cart_items_count', 0)
        in_checkout = context.get_state('checkout') is not None

        return f"""You are a routing agent for an e-commerce assistant.

Your job: Classify user intent and route to the right specialist agent.

AVAILABLE AGENTS:
1. **product_discovery** - Product search, recommendations, browsing, questions about products
2. **cart** - Add/remove items, view cart, modify quantities
3. **checkout** - Complete order, payment, shipping address

CURRENT STATE:
- Cart items: {cart_count}
- In checkout: {in_checkout}

CLASSIFICATION RULES:
- Product queries (search, find, show, what, which, recommend, gift, looking for) → product_discovery
- Cart actions (add, buy, remove, view cart, update quantity) → cart
- Checkout/payment (checkout, pay, complete, address, shipping) → checkout
- Greetings/general questions → product_discovery (they handle general queries)

RESPONSE FORMAT (JSON only):
{{
    "agent": "product_discovery|cart|checkout",
    "confidence": 0.0-1.0,
    "reason": "brief explanation",
    "needs_clarification": false,
    "clarification_question": null
}}

CLARIFICATION RULES:
- If intent is ambiguous (confidence < 0.7), ask clarifying question
- If cart is empty and user wants checkout, suggest adding items first
- If user says "help" or unclear message, ask what they need

Now classify the user's message:"""

    def get_tools(self):
        """Router doesn't use tools - pure classification."""
        return []

    def should_handoff(self, user_message: str, context: AgentContext) -> Optional[Dict]:
        """Router always hands off to specialists - it never handles requests itself."""
        return None  # Handled in _generate_response

    def _generate_response(self, context: AgentContext) -> AgentResponse:
        """
        Classify intent and route to appropriate agent.

        Returns:
            AgentResponse with handoff_to set to target agent
        """
        # Initialize LLM
        self._initialize_llm()

        # Build messages
        system_prompt = self.get_system_prompt(context)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=context.user_message)
        ]

        # Get classification from Haiku
        try:
            response = self.llm.invoke(messages)
            classification = self._parse_classification(response.content)

            # Handle clarification needed
            if classification.get('needs_clarification'):
                return AgentResponse(
                    content=classification.get('clarification_question',
                                             "Could you please clarify what you'd like help with?"),
                    needs_clarification=True,
                    metadata={
                        'agent': 'router',
                        'confidence': classification.get('confidence', 0.0),
                        'reason': classification.get('reason', '')
                    }
                )

            # Route to specialist
            target_agent = classification.get('agent', 'product_discovery')
            confidence = classification.get('confidence', 0.0)
            reason = classification.get('reason', 'Intent classification')

            return AgentResponse(
                content=f"Routing to {target_agent}...",
                handoff_to=target_agent,
                handoff_reason=reason,
                metadata={
                    'agent': 'router',
                    'confidence': confidence,
                    'reason': reason,
                    'classification': classification
                }
            )

        except Exception as e:
            # Fallback: route to product discovery (safest default)
            return AgentResponse(
                content="Routing to product discovery...",
                handoff_to='product_discovery',
                handoff_reason='Router error - fallback to product discovery',
                metadata={
                    'agent': 'router',
                    'error': str(e),
                    'confidence': 0.5
                }
            )

    def _parse_classification(self, response_content: str) -> Dict:
        """
        Parse JSON classification from LLM response.

        Args:
            response_content: LLM response string

        Returns:
            Classification dict
        """
        try:
            # Try to extract JSON from response
            # Handle cases where LLM adds extra text
            json_match = re.search(r'\{[^{}]*\}', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # No JSON found, try parsing entire response
                return json.loads(response_content)

        except json.JSONDecodeError:
            # Fallback: parse manually
            return self._manual_parse(response_content)

    def _manual_parse(self, response: str) -> Dict:
        """
        Manual parsing fallback if JSON parsing fails.

        Args:
            response: LLM response string

        Returns:
            Classification dict with defaults
        """
        response_lower = response.lower()

        # Detect agent mention
        if 'product_discovery' in response_lower or 'product' in response_lower:
            agent = 'product_discovery'
        elif 'cart' in response_lower:
            agent = 'cart'
        elif 'checkout' in response_lower:
            agent = 'checkout'
        else:
            agent = 'product_discovery'  # Default

        # Detect confidence
        confidence = 0.7  # Default medium confidence
        if 'high' in response_lower or '0.9' in response_lower or '0.8' in response_lower:
            confidence = 0.9
        elif 'low' in response_lower or '0.5' in response_lower or '0.6' in response_lower:
            confidence = 0.6

        # Detect clarification needed
        needs_clarification = 'clarification' in response_lower or 'unclear' in response_lower

        return {
            'agent': agent,
            'confidence': confidence,
            'reason': 'Manual parse fallback',
            'needs_clarification': needs_clarification,
            'clarification_question': None
        }

    def classify_intent(self, user_message: str, session_context: Dict = None) -> Dict:
        """
        Convenience method for testing: classify intent without full agent context.

        Args:
            user_message: User's message
            session_context: Optional session context dict

        Returns:
            Classification dict with agent, confidence, reason
        """
        # Build minimal context
        context = AgentContext(
            session_id='test',
            user_message=user_message,
            conversation_history=[],
            session_state=session_context or {},
            user_context={}
        )

        # Generate response
        response = self._generate_response(context)

        # Extract classification
        return {
            'agent': response.handoff_to or 'product_discovery',
            'confidence': response.metadata.get('confidence', 0.0),
            'reason': response.handoff_reason or '',
            'needs_clarification': response.needs_clarification
        }
