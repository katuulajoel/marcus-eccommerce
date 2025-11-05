"""
Base Agent Abstract Class
All specialized agents inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


@dataclass
class AgentResponse:
    """
    Standardized response from any agent.
    """
    content: str  # The actual response text
    handoff_to: Optional[str] = None  # Agent to hand off to (e.g., "cart", "checkout")
    handoff_reason: Optional[str] = None  # Why handoff is needed
    metadata: Dict[str, Any] = None  # Additional info (tools used, products found, etc.)
    needs_clarification: bool = False  # Agent needs more info from user
    clarification_question: Optional[str] = None  # Question to ask user

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AgentContext:
    """
    Context passed to each agent containing session state and conversation history.
    """
    session_id: str
    user_message: str
    conversation_history: List[Dict]  # Previous messages
    session_state: Dict  # Redis state (cart, checkout, etc.)
    user_context: Dict  # Page, category, product being viewed, etc.

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get value from session state."""
        return self.session_state.get(key, default)

    def get_user_context(self, key: str, default: Any = None) -> Any:
        """Get value from user context."""
        return self.user_context.get(key, default)


class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Each agent is an expert in a specific domain.
    """

    def __init__(self, model_name: str = "claude-sonnet-4-20250514", temperature: float = 0.7):
        """
        Initialize agent with LLM.

        Args:
            model_name: Claude model to use (sonnet or haiku)
            temperature: LLM temperature (0-1)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self._initialized = False

    def _initialize_llm(self):
        """Lazy initialization of LLM."""
        if self._initialized:
            return

        claude_api_key = os.getenv('CLAUDE_API_KEY')
        if not claude_api_key:
            raise ValueError("CLAUDE_API_KEY environment variable not set")

        self.llm = ChatAnthropic(
            model=self.model_name,
            temperature=self.temperature,
            api_key=claude_api_key,
            max_tokens=1024  # Reduced from 4096 to save costs and avoid rate limits
        )

        self._initialized = True

    @abstractmethod
    def get_system_prompt(self, context: AgentContext) -> str:
        """
        Get the system prompt for this agent.
        Must be implemented by each specialized agent.

        Should be concise (target: 300-500 tokens, max 800 tokens).

        Args:
            context: Current session context

        Returns:
            System prompt string
        """
        pass

    @abstractmethod
    def get_tools(self) -> List:
        """
        Get LangChain tools this agent can use.
        Must be implemented by each specialized agent.

        Returns:
            List of LangChain tool instances
        """
        pass

    @abstractmethod
    def should_handoff(self, user_message: str, context: AgentContext) -> Optional[Dict]:
        """
        Determine if this agent should hand off to another agent.
        Must be implemented by each specialized agent.

        Args:
            user_message: User's current message
            context: Session context

        Returns:
            Dict with 'agent' and 'reason' if handoff needed, None otherwise
        """
        pass

    @property
    @abstractmethod
    def agent_name(self) -> str:
        """
        Name of this agent (e.g., 'product_discovery', 'cart', 'checkout').
        Must be implemented by each specialized agent.
        """
        pass

    @property
    @abstractmethod
    def agent_description(self) -> str:
        """
        Description of what this agent does (for router).
        Must be implemented by each specialized agent.
        """
        pass

    def process(self, context: AgentContext) -> AgentResponse:
        """
        Process user message and generate response.
        This is the main entry point for all agents.

        Args:
            context: Full agent context with message, history, state

        Returns:
            AgentResponse with content and metadata
        """
        # Initialize LLM if not done yet
        self._initialize_llm()

        # Check if should hand off to another agent
        handoff = self.should_handoff(context.user_message, context)
        if handoff:
            return AgentResponse(
                content=f"Let me connect you with the {handoff['agent']} specialist...",
                handoff_to=handoff['agent'],
                handoff_reason=handoff['reason']
            )

        try:
            # Generate response using agent's logic
            return self._generate_response(context)

        except Exception as e:
            # Graceful error handling
            return AgentResponse(
                content=f"I apologize, but I encountered an error: {str(e)}. Could you please rephrase your question?",
                metadata={"error": str(e), "agent": self.agent_name}
            )

    @abstractmethod
    def _generate_response(self, context: AgentContext) -> AgentResponse:
        """
        Generate agent-specific response.
        Must be implemented by each specialized agent.

        This is where the agent's core logic lives:
        - Use tools if needed
        - Call LLM with system prompt
        - Format response

        Args:
            context: Full agent context

        Returns:
            AgentResponse
        """
        pass

    def _format_conversation_history(self, history: List[Dict]) -> List:
        """
        Convert conversation history to LangChain message format.

        Args:
            history: List of message dicts with 'role' and 'content'

        Returns:
            List of LangChain messages
        """
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

    def _build_input_with_context(self, user_message: str, context: AgentContext) -> str:
        """
        Enhance user message with relevant context.

        Args:
            user_message: User's message
            context: Session context

        Returns:
            Enhanced message string
        """
        context_parts = []

        # Session ID (important for cart/checkout tools)
        if context.session_id:
            context_parts.append(f"Session ID: {context.session_id}")

        # Current page
        current_page = context.get_user_context('currentPage')
        if current_page:
            context_parts.append(f"User is on page: {current_page}")

        # Category context
        category_id = context.get_user_context('categoryId')
        if category_id:
            context_parts.append(f"Viewing category ID: {category_id}")

        # Product context
        product_id = context.get_user_context('productId')
        if product_id:
            context_parts.append(f"Looking at product ID: {product_id}")

        # Configuration context
        configuration = context.get_user_context('configuration')
        if configuration:
            context_parts.append(f"Current configuration: {configuration}")

        # Checkout state
        checkout_state = context.get_state('checkout')
        if checkout_state:
            context_parts.append(f"Checkout status: {checkout_state.get('status', 'in_progress')}")

        if context_parts:
            context_str = "\n".join(context_parts)
            return f"[Context: {context_str}]\n\nUser: {user_message}"

        return user_message

    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.agent_name}, model={self.model_name})>"
