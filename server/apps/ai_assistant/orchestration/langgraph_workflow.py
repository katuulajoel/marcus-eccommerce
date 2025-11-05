"""
LangGraph Multi-Agent Workflow
Orchestrates Router + Specialist Agents using state machine.
"""

from typing import Dict, TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import logging

from ..agents.router_agent import RouterAgent
from ..agents.product_agent import ProductDiscoveryAgent
from ..agents.cart_agent import CartManagementAgent
from ..agents.checkout_agent import CheckoutPaymentAgent
from ..agents.base_agent import AgentContext, AgentResponse
from .state_manager import get_state_manager
from .handoff_manager import get_handoff_manager

logger = logging.getLogger(__name__)


# Define workflow state
class AgentState(TypedDict):
    """
    State that flows through the agent workflow.
    """
    # Input
    session_id: str
    user_message: str
    conversation_history: list
    session_state: dict
    user_context: dict

    # Workflow state
    current_agent: str
    agent_response: str
    handoff_to: str | None
    handoff_reason: str | None
    metadata: dict

    # Iteration control
    iteration_count: int
    max_iterations: int


class MultiAgentWorkflow:
    """
    LangGraph workflow that orchestrates multiple agents.
    Manages routing, handoffs, and state.
    """

    def __init__(self):
        """Initialize workflow with all agents."""
        # Create agent instances
        self.router = RouterAgent()
        self.product_agent = ProductDiscoveryAgent()
        self.cart_agent = CartManagementAgent()
        self.checkout_agent = CheckoutPaymentAgent()

        # Create workflow graph
        self.workflow = self._build_workflow()

        # Agent mapping
        self.agents = {
            'router': self.router,
            'product_discovery': self.product_agent,
            'cart': self.cart_agent,
            'checkout': self.checkout_agent,
        }

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph state machine.

        Flow:
        1. Start → Router
        2. Router → [Product/Cart/Checkout] (based on intent)
        3. Specialist → [Another Specialist] or END
        """
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("router", self._router_node)
        workflow.add_node("product_discovery", self._product_node)
        workflow.add_node("cart", self._cart_node)
        workflow.add_node("checkout", self._checkout_node)

        # Entry point: always start at router
        workflow.set_entry_point("router")

        # Router edges (conditional based on classification)
        workflow.add_conditional_edges(
            "router",
            self._route_after_router,
            {
                "product_discovery": "product_discovery",
                "cart": "cart",
                "checkout": "checkout",
                "end": END,
            }
        )

        # Product agent edges (can hand off to cart/checkout or end)
        workflow.add_conditional_edges(
            "product_discovery",
            self._route_after_specialist,
            {
                "cart": "cart",
                "checkout": "checkout",
                "product_discovery": "product_discovery",
                "end": END,
            }
        )

        # Cart agent edges (can hand off to product/checkout or end)
        workflow.add_conditional_edges(
            "cart",
            self._route_after_specialist,
            {
                "product_discovery": "product_discovery",
                "checkout": "checkout",
                "cart": "cart",
                "end": END,
            }
        )

        # Checkout agent edges (can hand off to cart/product or end)
        workflow.add_conditional_edges(
            "checkout",
            self._route_after_specialist,
            {
                "cart": "cart",
                "product_discovery": "product_discovery",
                "checkout": "checkout",
                "end": END,
            }
        )

        return workflow.compile()

    def _router_node(self, state: AgentState) -> AgentState:
        """
        Router node: Classify intent and route to specialist.
        """
        logger.info(f"Router processing message: {state['user_message'][:50]}...")

        # Build agent context
        context = AgentContext(
            session_id=state['session_id'],
            user_message=state['user_message'],
            conversation_history=state['conversation_history'],
            session_state=state['session_state'],
            user_context=state['user_context']
        )

        # Process with router
        response = self.router.process(context)

        # Update state
        state['current_agent'] = 'router'
        state['agent_response'] = response.content
        state['handoff_to'] = response.handoff_to
        state['handoff_reason'] = response.handoff_reason
        state['metadata'] = response.metadata
        state['iteration_count'] = state.get('iteration_count', 0) + 1

        # Update state manager
        state_manager = get_state_manager(state['session_id'])
        state_manager.set_current_agent('router')

        logger.info(f"Router classified intent → {response.handoff_to} (confidence: {response.metadata.get('confidence', 0):.2f})")

        return state

    def _product_node(self, state: AgentState) -> AgentState:
        """
        Product discovery node.
        """
        logger.info("Product agent processing request...")
        return self._specialist_node(state, 'product_discovery', self.product_agent)

    def _cart_node(self, state: AgentState) -> AgentState:
        """
        Cart management node.
        """
        logger.info("Cart agent processing request...")
        return self._specialist_node(state, 'cart', self.cart_agent)

    def _checkout_node(self, state: AgentState) -> AgentState:
        """
        Checkout node.
        """
        logger.info("Checkout agent processing request...")
        return self._specialist_node(state, 'checkout', self.checkout_agent)

    def _specialist_node(self, state: AgentState, agent_name: str, agent) -> AgentState:
        """
        Generic specialist node handler.
        """
        # Build agent context
        context = AgentContext(
            session_id=state['session_id'],
            user_message=state['user_message'],
            conversation_history=state['conversation_history'],
            session_state=state['session_state'],
            user_context=state['user_context']
        )

        # Process with specialist agent
        response = agent.process(context)

        # Update state
        state['current_agent'] = agent_name
        state['agent_response'] = response.content
        state['handoff_to'] = response.handoff_to
        state['handoff_reason'] = response.handoff_reason
        state['metadata'] = response.metadata
        state['iteration_count'] = state.get('iteration_count', 0) + 1

        # Update state manager
        state_manager = get_state_manager(state['session_id'])
        state_manager.set_current_agent(agent_name)
        state_manager.add_agent_to_history(agent_name)

        if response.handoff_to:
            logger.info(f"{agent_name} requesting handoff → {response.handoff_to}")
            state_manager.set_handoff_context({
                'from': agent_name,
                'to': response.handoff_to,
                'reason': response.handoff_reason
            })

        return state

    def _route_after_router(self, state: AgentState) -> str:
        """
        Decide where to route after router classification.
        """
        target = state.get('handoff_to')

        if not target:
            logger.warning("Router did not specify handoff target, ending")
            return "end"

        if target in ['product_discovery', 'cart', 'checkout']:
            return target

        logger.warning(f"Unknown target from router: {target}, defaulting to product_discovery")
        return "product_discovery"

    def _route_after_specialist(self, state: AgentState) -> str:
        """
        Decide where to route after specialist processes request.
        """
        # Check iteration limit (prevent infinite loops)
        max_iterations = state.get('max_iterations', 5)
        iteration_count = state.get('iteration_count', 0)

        if iteration_count >= max_iterations:
            logger.warning(f"Max iterations ({max_iterations}) reached, ending workflow")
            return "end"

        # Check if specialist requested handoff
        target = state.get('handoff_to')

        if not target:
            # No handoff requested, end workflow
            return "end"

        # Validate handoff
        current_agent = state['current_agent']
        handoff_manager = get_handoff_manager()

        if handoff_manager.should_allow_handoff(
            from_agent=current_agent,
            to_agent=target,
            reason=state.get('handoff_reason', ''),
            current_context=state['session_state']
        ):
            logger.info(f"Handoff approved: {current_agent} → {target}")
            return target
        else:
            logger.warning(f"Handoff blocked: {current_agent} → {target}")
            return "end"

    def run(
        self,
        session_id: str,
        user_message: str,
        conversation_history: list = None,
        user_context: dict = None
    ) -> Dict:
        """
        Run the multi-agent workflow.

        Args:
            session_id: Session identifier
            user_message: User's message
            conversation_history: Previous conversation messages
            user_context: User context (page, category, etc.)

        Returns:
            Dict with response content and metadata
        """
        # Get state manager
        state_manager = get_state_manager(session_id)
        session_state = state_manager.get_state()

        # Initialize state
        initial_state: AgentState = {
            'session_id': session_id,
            'user_message': user_message,
            'conversation_history': conversation_history or [],
            'session_state': session_state,
            'user_context': user_context or {},
            'current_agent': 'router',
            'agent_response': '',
            'handoff_to': None,
            'handoff_reason': None,
            'metadata': {},
            'iteration_count': 0,
            'max_iterations': 5,
        }

        try:
            # Run workflow
            logger.info(f"Starting workflow for session {session_id}")
            final_state = self.workflow.invoke(initial_state)

            # Extract response
            response_content = final_state.get('agent_response', '')
            metadata = final_state.get('metadata', {})

            # Add workflow metadata
            metadata['workflow'] = {
                'iterations': final_state.get('iteration_count', 0),
                'final_agent': final_state.get('current_agent'),
                'agent_history': state_manager.get_agent_history(),
            }

            logger.info(f"Workflow completed: {final_state.get('iteration_count', 0)} iterations, final agent: {final_state.get('current_agent')}")

            return {
                'content': response_content,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"Workflow error: {str(e)}", exc_info=True)
            return {
                'content': "I apologize, but I encountered an error processing your request. Could you please try again?",
                'metadata': {
                    'error': str(e),
                    'workflow': 'error'
                }
            }


# Global instance
_workflow_instance = None


def get_multi_agent_workflow() -> MultiAgentWorkflow:
    """
    Get or create the global MultiAgentWorkflow instance.

    Returns:
        MultiAgentWorkflow instance
    """
    global _workflow_instance

    if _workflow_instance is None:
        _workflow_instance = MultiAgentWorkflow()
        logger.info("Multi-agent workflow initialized")

    return _workflow_instance
