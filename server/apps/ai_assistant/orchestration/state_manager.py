"""
State Manager for Multi-Agent System
Manages shared state across agents using Redis.
"""

import json
from typing import Dict, Any, Optional
from django.core.cache import cache


class StateManager:
    """
    Manages session state for multi-agent conversations.
    Uses Redis for persistence across agent handoffs.
    """

    def __init__(self, session_id: str):
        """
        Initialize state manager for a session.

        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.state_key = f"agent_state:{session_id}"
        self.ttl = 86400  # 24 hours (longer than checkout's 1 hour)

    def get_state(self) -> Dict[str, Any]:
        """
        Get entire session state.

        Returns:
            Dict containing all session state
        """
        state_json = cache.get(self.state_key)
        if state_json:
            try:
                return json.loads(state_json)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_state(self, state: Dict[str, Any]):
        """
        Replace entire session state.

        Args:
            state: New state dict
        """
        state_json = json.dumps(state)
        cache.set(self.state_key, state_json, timeout=self.ttl)

    def update_state(self, updates: Dict[str, Any]):
        """
        Update specific keys in session state.

        Args:
            updates: Dict with keys to update
        """
        current_state = self.get_state()
        current_state.update(updates)
        self.set_state(current_state)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get specific value from state.

        Args:
            key: State key
            default: Default value if key not found

        Returns:
            Value from state or default
        """
        state = self.get_state()
        return state.get(key, default)

    def set(self, key: str, value: Any):
        """
        Set specific value in state.

        Args:
            key: State key
            value: Value to set
        """
        self.update_state({key: value})

    def delete(self, key: str):
        """
        Delete specific key from state.

        Args:
            key: State key to delete
        """
        state = self.get_state()
        if key in state:
            del state[key]
            self.set_state(state)

    def clear(self):
        """Clear all session state."""
        cache.delete(self.state_key)

    # Agent-specific state helpers

    def get_current_agent(self) -> Optional[str]:
        """
        Get the currently active agent.

        Returns:
            Agent name or None
        """
        return self.get('current_agent')

    def set_current_agent(self, agent_name: str):
        """
        Set the currently active agent.

        Args:
            agent_name: Name of active agent
        """
        self.set('current_agent', agent_name)

    def get_agent_history(self) -> list:
        """
        Get history of agents used in this session.

        Returns:
            List of agent names in order used
        """
        return self.get('agent_history', [])

    def add_agent_to_history(self, agent_name: str):
        """
        Add agent to usage history.

        Args:
            agent_name: Name of agent to add
        """
        history = self.get_agent_history()
        history.append(agent_name)
        self.set('agent_history', history)

    def get_handoff_context(self) -> Optional[Dict]:
        """
        Get context from previous agent handoff.

        Returns:
            Handoff context dict or None
        """
        return self.get('handoff_context')

    def set_handoff_context(self, context: Dict):
        """
        Set context for next agent during handoff.

        Args:
            context: Context dict to pass to next agent
        """
        self.set('handoff_context', context)

    def clear_handoff_context(self):
        """Clear handoff context after it's been used."""
        self.delete('handoff_context')

    # Checkout-specific state helpers

    def get_checkout_state(self) -> Optional[Dict]:
        """
        Get checkout session state.

        Returns:
            Checkout state dict or None
        """
        return self.get('checkout')

    def set_checkout_state(self, checkout_state: Dict):
        """
        Set checkout session state.

        Args:
            checkout_state: Checkout state dict
        """
        self.set('checkout', checkout_state)

    def is_in_checkout(self) -> bool:
        """
        Check if session is currently in checkout flow.

        Returns:
            True if in checkout, False otherwise
        """
        checkout = self.get_checkout_state()
        return checkout is not None and checkout.get('status') != 'completed'

    # Cart-specific state helpers

    def get_cart_items_count(self) -> int:
        """
        Get number of items in cart.

        Returns:
            Cart item count
        """
        # This should query CartService, but for now return cached value
        return self.get('cart_items_count', 0)

    def set_cart_items_count(self, count: int):
        """
        Set cart items count (for quick access without querying Redis).

        Args:
            count: Number of items in cart
        """
        self.set('cart_items_count', count)

    # Conversation flow helpers

    def get_last_intent(self) -> Optional[str]:
        """
        Get the last detected user intent.

        Returns:
            Intent string or None
        """
        return self.get('last_intent')

    def set_last_intent(self, intent: str):
        """
        Set the last detected user intent.

        Args:
            intent: Intent string
        """
        self.set('last_intent', intent)

    def get_clarification_state(self) -> Optional[Dict]:
        """
        Get state for multi-turn clarification flows.

        Returns:
            Clarification state dict or None
        """
        return self.get('clarification')

    def set_clarification_state(self, state: Dict):
        """
        Set state for multi-turn clarification.

        Args:
            state: Clarification state (what we're asking about, options, etc.)
        """
        self.set('clarification', state)

    def clear_clarification_state(self):
        """Clear clarification state after it's resolved."""
        self.delete('clarification')

    def __repr__(self):
        return f"<StateManager(session={self.session_id})>"


# Global cache for state managers (avoid recreating for same session)
_state_manager_cache: Dict[str, StateManager] = {}


def get_state_manager(session_id: str) -> StateManager:
    """
    Get or create StateManager for a session.
    Uses in-memory cache to avoid recreating managers.

    Args:
        session_id: Session identifier

    Returns:
        StateManager instance
    """
    if session_id not in _state_manager_cache:
        _state_manager_cache[session_id] = StateManager(session_id)
    return _state_manager_cache[session_id]
