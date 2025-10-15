"""
LangChain Agent Service
Replaces the hardcoded llm_service with an intelligent agent that uses tools.
NO HARDCODED KEYWORDS - Agent learns from database through tools!
"""

import os
from typing import Dict, List
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
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

        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=openai_api_key
        )

        # Get dynamic tools (powered by database!)
        tools = get_all_tools()

        # Create dynamic system prompt (no hardcoded domain knowledge!)
        system_prompt = self._build_dynamic_system_prompt()

        # Create prompt template with tool integration
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate",
            handle_parsing_errors=True
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

IMPORTANT GUIDELINES:
1. **Use Tools Actively**: Don't guess - use your tools to get accurate, real-time information from the database
2. **Be Conversational**: Have natural conversations, ask clarifying questions when needed
3. **Product Recommendations**: Use search_products tool to find items matching user needs
4. **Configuration Help**: Use validate_configuration when discussing custom builds
5. **Pricing**: Use get_price_range and get_part_options for accurate pricing
6. **Stock**: Always mention stock status when recommending products
7. **No Hallucination**: Only recommend products that exist in search results

CONVERSATION STYLE:
- Friendly and helpful, like a knowledgeable sales associate
- Ask follow-up questions to understand needs better
- Explain technical details in simple terms
- Proactively suggest relevant products
- Help users make informed decisions

WHEN USER ASKS ABOUT:
- Products → Use search_products tool
- Categories → Use search_categories or get_available_categories
- Customization → Use get_part_options and validate_configuration
- Pricing → Use get_price_range and search_products
- Compatibility → Use validate_configuration

Remember: You're here to help users find and customize the perfect product!
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

            # Run agent
            result = self.agent_executor.invoke({
                "input": full_input,
                "chat_history": chat_history
            })

            # Extract response
            response_text = result.get('output', '')

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
