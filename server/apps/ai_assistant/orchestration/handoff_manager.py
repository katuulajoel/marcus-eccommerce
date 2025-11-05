"""
Handoff Manager for Multi-Agent System
Manages transitions between specialized agents.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class HandoffRequest:
    """
    Request to hand off conversation to another agent.
    """
    from_agent: str  # Agent making the handoff
    to_agent: str  # Target agent
    reason: str  # Why handoff is needed
    context: Dict[str, Any]  # Context to pass to next agent
    user_message: Optional[str] = None  # Optional message to pass


class HandoffManager:
    """
    Manages agent handoffs and validates transitions.
    Ensures agents can only hand off to appropriate targets.
    """

    # Valid handoff rules: source_agent -> [allowed_target_agents]
    HANDOFF_RULES = {
        'router': ['product_discovery', 'cart', 'checkout'],  # Router can go anywhere
        'product_discovery': ['cart', 'checkout'],  # Product can suggest cart/checkout
        'cart': ['product_discovery', 'checkout'],  # Cart can go back to products or forward to checkout
        'checkout': ['cart', 'product_discovery'],  # Checkout can go back if needed
    }

    # Agent priorities (higher number = more specialized/final in flow)
    AGENT_PRIORITY = {
        'router': 0,
        'product_discovery': 1,
        'cart': 2,
        'checkout': 3,
    }

    def __init__(self):
        """Initialize handoff manager."""
        self.handoff_history = []

    def validate_handoff(self, handoff: HandoffRequest) -> bool:
        """
        Validate if a handoff is allowed.

        Args:
            handoff: HandoffRequest to validate

        Returns:
            True if valid, False otherwise
        """
        # Check if source agent exists in rules
        if handoff.from_agent not in self.HANDOFF_RULES:
            logger.warning(f"Unknown source agent: {handoff.from_agent}")
            return False

        # Check if target agent is allowed
        allowed_targets = self.HANDOFF_RULES.get(handoff.from_agent, [])
        if handoff.to_agent not in allowed_targets:
            logger.warning(
                f"Invalid handoff: {handoff.from_agent} -> {handoff.to_agent}. "
                f"Allowed: {allowed_targets}"
            )
            return False

        return True

    def should_allow_handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        current_context: Dict
    ) -> bool:
        """
        Determine if handoff should be allowed based on context.

        Args:
            from_agent: Source agent
            to_agent: Target agent
            reason: Reason for handoff
            current_context: Current session context

        Returns:
            True if handoff should proceed
        """
        # Create handoff request
        handoff = HandoffRequest(
            from_agent=from_agent,
            to_agent=to_agent,
            reason=reason,
            context=current_context
        )

        # Basic validation
        if not self.validate_handoff(handoff):
            return False

        # Additional context-based validation

        # Don't hand off to cart if cart is empty (unless explicitly adding to cart)
        if to_agent == 'cart':
            cart_count = current_context.get('cart_items_count', 0)
            if cart_count == 0 and 'add' not in reason.lower():
                logger.info(f"Blocking handoff to cart: cart is empty")
                return False

        # Don't hand off to checkout if cart is empty
        if to_agent == 'checkout':
            cart_count = current_context.get('cart_items_count', 0)
            if cart_count == 0:
                logger.info(f"Blocking handoff to checkout: cart is empty")
                return False

        # Don't allow going back in flow unless there's a good reason
        from_priority = self.AGENT_PRIORITY.get(from_agent, 0)
        to_priority = self.AGENT_PRIORITY.get(to_agent, 0)

        if to_priority < from_priority:
            # Going backwards - check if reason is valid
            backward_reasons = ['cart empty', 'need more items', 'modify order', 'change items']
            if not any(keyword in reason.lower() for keyword in backward_reasons):
                logger.info(
                    f"Blocking backward handoff ({from_agent} -> {to_agent}): "
                    f"reason not valid for going back"
                )
                return False

        return True

    def execute_handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        context: Dict,
        user_message: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Execute a handoff from one agent to another.

        Args:
            from_agent: Source agent name
            to_agent: Target agent name
            reason: Reason for handoff
            context: Context to pass
            user_message: Optional message to pass

        Returns:
            Handoff result dict if successful, None if blocked
        """
        # Validate handoff
        if not self.should_allow_handoff(from_agent, to_agent, reason, context):
            return None

        # Create handoff
        handoff = HandoffRequest(
            from_agent=from_agent,
            to_agent=to_agent,
            reason=reason,
            context=context,
            user_message=user_message
        )

        # Log handoff
        self.handoff_history.append(handoff)
        logger.info(f"✓ Handoff: {from_agent} -> {to_agent} (reason: {reason})")

        # Return handoff details
        return {
            'to_agent': to_agent,
            'reason': reason,
            'context': context,
            'user_message': user_message
        }

    def get_handoff_context(self, handoff_result: Dict) -> Dict:
        """
        Extract context for next agent from handoff result.

        Args:
            handoff_result: Result from execute_handoff

        Returns:
            Context dict for next agent
        """
        return {
            'handoff_reason': handoff_result['reason'],
            'previous_agent': handoff_result.get('previous_agent'),
            'user_message': handoff_result.get('user_message'),
            **handoff_result.get('context', {})
        }

    def suggest_next_agent(
        self,
        current_agent: str,
        user_message: str,
        session_context: Dict
    ) -> Optional[str]:
        """
        Suggest which agent to hand off to based on user message.

        Args:
            current_agent: Current agent name
            user_message: User's message
            session_context: Current session context

        Returns:
            Suggested agent name or None
        """
        message_lower = user_message.lower()

        # Cart-related keywords
        cart_keywords = ['add to cart', 'add it', 'buy', 'purchase', 'order', 'cart', 'basket']
        if any(keyword in message_lower for keyword in cart_keywords):
            if current_agent != 'cart':
                return 'cart'

        # Checkout-related keywords
        checkout_keywords = ['checkout', 'pay', 'payment', 'complete order', 'finish', 'proceed']
        if any(keyword in message_lower for keyword in checkout_keywords):
            if current_agent != 'checkout':
                # Only suggest checkout if cart has items
                if session_context.get('cart_items_count', 0) > 0:
                    return 'checkout'

        # Product-related keywords
        product_keywords = ['show me', 'find', 'search', 'looking for', 'recommend', 'what', 'which']
        if any(keyword in message_lower for keyword in product_keywords):
            if current_agent != 'product_discovery':
                return 'product_discovery'

        return None

    def get_handoff_summary(self) -> Dict:
        """
        Get summary of handoffs in current session.

        Returns:
            Dict with handoff statistics
        """
        if not self.handoff_history:
            return {'total_handoffs': 0}

        agent_counts = {}
        for handoff in self.handoff_history:
            agent_counts[handoff.to_agent] = agent_counts.get(handoff.to_agent, 0) + 1

        return {
            'total_handoffs': len(self.handoff_history),
            'agent_usage': agent_counts,
            'last_handoff': self.handoff_history[-1].to_agent if self.handoff_history else None
        }

    def __repr__(self):
        return f"<HandoffManager(handoffs={len(self.handoff_history)})>"


# Global instance
_handoff_manager_instance = None


def get_handoff_manager() -> HandoffManager:
    """
    Get global HandoffManager instance.

    Returns:
        HandoffManager instance
    """
    global _handoff_manager_instance
    if _handoff_manager_instance is None:
        _handoff_manager_instance = HandoffManager()
    return _handoff_manager_instance
