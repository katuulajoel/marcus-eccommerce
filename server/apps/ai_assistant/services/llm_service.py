"""
LLM Service for AI Assistant
Handles integration with OpenAI API for intelligent responses
"""

import os
import json
from typing import List, Dict, Optional

# For now, we'll create a framework that can work without OpenAI installed
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMService:
    """
    Service for generating AI responses using Large Language Models.
    Supports OpenAI GPT models with fallback to keyword-based responses.
    """

    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')  # Use cheaper model for faster responses
        self.temperature = float(os.environ.get('OPENAI_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.environ.get('OPENAI_MAX_TOKENS', '800'))

        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            self.use_openai = True
        else:
            self.use_openai = False
            self.client = None

    def generate_response(
        self,
        user_message: str,
        context: Dict,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate an AI response based on user message and context.

        Args:
            user_message: The user's input message
            context: Dictionary containing session context (page, cart, configuration)
            conversation_history: List of previous messages in the conversation

        Returns:
            Dictionary with response content and metadata
        """
        if self.use_openai:
            return self._generate_openai_response(user_message, context, conversation_history)
        else:
            return self._generate_fallback_response(user_message, context)

    def _generate_openai_response(
        self,
        user_message: str,
        context: Dict,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """Generate response using OpenAI API"""
        try:
            # Build system prompt with context
            system_prompt = self._build_system_prompt(context)

            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Call OpenAI API (new v1.x+ syntax)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            content = response.choices[0].message.content
            metadata = {
                "actionType": self._determine_action_type(content, context),
                "model": self.model,
                "tokens_used": response.usage.total_tokens
            }

            return {
                "content": content,
                "metadata": metadata
            }

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_fallback_response(user_message, context)

    def _build_system_prompt(self, context: Dict) -> str:
        """Build system prompt with context information"""
        prompt = """You are an AI assistant for Marcus Gift Shop, an e-commerce platform
specializing in personalized and custom gift items. Your role is to help customers find
the perfect gifts and guide them through the customization process.

Key responsibilities:
1. Recommend gifts based on occasion, recipient, and budget
2. Explain product features and customization options with SPECIFIC PRICES
3. Guide customers through the personalization process
4. Answer questions about compatibility between items in gift sets
5. Provide EXACT pricing information and budget guidance using the product catalog
6. Assist with shipping, payments, and order inquiries

CRITICAL: UNDERSTAND THE DIFFERENCE BETWEEN PRECONFIGURED PRODUCTS vs CUSTOM CONFIGURATIONS

1. **PRECONFIGURED PRODUCTS** (in 'preconfigured_products' section):
   - These are pre-built gift sets created by the admin
   - The 'total_price' is the FINAL price - DO NOT add part prices again
   - Use these when customer asks "what products do you have?" or "show me explosion boxes"
   - Example: "The Boyfriend Kit" at UGX 370,000 (total_price) is ready to buy

2. **CUSTOM CONFIGURATIONS** (in 'cheapest_custom_configs' / 'most_expensive_custom_configs'):
   - These are built by selecting the cheapest/most expensive option for EACH part
   - The 'total_cost' is calculated by summing all selected part option prices
   - Use these when customer asks "cheapest configuration" or "most expensive I can build"
   - Example: Cheapest Explosion Box = Box Design (UGX 50k) + Filler (UGX 35k) = UGX 85k total

IMPORTANT QUERY HANDLING:
- "what's the cheapest configuration?" → Use 'cheapest_custom_configs', explain which options to select
- "show me your cheapest product" → Use 'preconfigured_products', find lowest total_price
- "most expensive I can build" → Use 'most_expensive_custom_configs', explain the build
- "what's your most expensive gift?" → Use 'preconfigured_products', find highest total_price

NEVER double-count prices! Preconfigured product total_price already includes everything.
"""

        # Add current user context
        if context:
            prompt += "\n\n=== USER CONTEXT ===\n"
            if context.get('currentPage'):
                prompt += f"- User is on page: {context['currentPage']}\n"
            if context.get('categoryId'):
                prompt += f"- Viewing category ID: {context['categoryId']}\n"
            if context.get('productId'):
                prompt += f"- Viewing product ID: {context['productId']}\n"
            if context.get('configuration'):
                prompt += f"- Current configuration: {json.dumps(context['configuration'], indent=2)}\n"
            if context.get('cartItems'):
                prompt += f"- Items in cart: {len(context['cartItems'])}\n"

        # Add PRECONFIGURED PRODUCTS (pre-built by admin)
        if context.get('preconfigured_products'):
            prompt += "\n\n=== PRECONFIGURED PRODUCTS (Admin Pre-Built Gift Sets) ===\n"
            prompt += "These are ready-to-buy products. The TOTAL PRICE already includes all parts.\n"
            for product in context['preconfigured_products']:
                prompt += f"\n{product['name']} (ID: {product['id']})\n"
                prompt += f"  Category: {product['category']}\n"
                prompt += f"  Configuration includes:\n"
                for part in product['parts']:
                    prompt += f"    - {part['part']}: {part['option']}\n"
                prompt += f"  **TOTAL PRICE: UGX {product['total_price']:,.0f}**\n"
                if product.get('description'):
                    prompt += f"  Description: {product['description']}\n"

        # Add CHEAPEST CUSTOM CONFIGURATIONS
        if context.get('cheapest_custom_configs'):
            prompt += "\n\n=== CHEAPEST CUSTOM CONFIGURATIONS (Build Your Own) ===\n"
            prompt += "These show the absolute cheapest way to build a gift in each category.\n"
            for category_name, config in context['cheapest_custom_configs'].items():
                prompt += f"\n{category_name}:\n"
                for part in config['parts']:
                    prompt += f"  - {part['part']}: {part['option']} (UGX {part['price']:,.0f})\n"
                prompt += f"  **TOTAL COST: UGX {config['total_cost']:,.0f}**\n"

        # Add MOST EXPENSIVE CUSTOM CONFIGURATIONS
        if context.get('most_expensive_custom_configs'):
            prompt += "\n\n=== MOST EXPENSIVE CUSTOM CONFIGURATIONS (Build Your Own) ===\n"
            prompt += "These show the most expensive way to build a gift in each category.\n"
            for category_name, config in context['most_expensive_custom_configs'].items():
                prompt += f"\n{category_name}:\n"
                for part in config['parts']:
                    prompt += f"  - {part['part']}: {part['option']} (UGX {part['price']:,.0f})\n"
                prompt += f"  **TOTAL COST: UGX {config['total_cost']:,.0f}**\n"

        # Add CONFIGURATION RULES
        if context.get('configuration_rules'):
            rules = context['configuration_rules']

            if rules.get('incompatibility_rules'):
                prompt += "\n\n=== INCOMPATIBILITY RULES ===\n"
                prompt += "These combinations CANNOT be selected together:\n"
                for rule in rules['incompatibility_rules']:
                    prompt += f"  ❌ {rule['option1']} + {rule['option2']}\n"
                    prompt += f"     Reason: {rule['message']}\n"

            if rules.get('price_adjustment_rules'):
                prompt += "\n\n=== PRICE ADJUSTMENT RULES ===\n"
                prompt += "When certain options are selected, other option prices change:\n"
                for rule in rules['price_adjustment_rules']:
                    adjustment_text = f"+UGX {rule['adjustment']:,.0f}" if rule['adjustment'] > 0 else f"UGX {rule['adjustment']:,.0f}"
                    symbol = "💰" if rule['type'] == 'premium' else "💸"
                    prompt += f"  {symbol} When you select '{rule['when_selected']}'\n"
                    prompt += f"     → '{rule['affects']}' price changes by {adjustment_text}\n"

            prompt += "\n⚠️ NOTE: The cheapest/most expensive configurations above already respect these rules!\n"

        # Add category parts and options
        if context.get('category_parts'):
            prompt += "\n\n=== AVAILABLE CUSTOMIZATION OPTIONS BY CATEGORY ===\n"
            for category_name, category_data in context['category_parts'].items():
                prompt += f"\n{category_name}:\n"
                for part in category_data['parts']:
                    prompt += f"  {part['name']} (Step {part['step']}):\n"
                    for option in part['options']:
                        in_stock = " [IN STOCK]" if option['in_stock'] else " [OUT OF STOCK]"
                        prompt += f"    - {option['name']}: UGX {option['price']:,.0f}{in_stock}\n"

        # Add category context if available
        if context.get('category_details'):
            prompt += f"\n\n=== CURRENT CATEGORY DETAILS ===\n"
            prompt += f"Category: {context['category_details']['category_name']}\n"
            prompt += f"Description: {context['category_details']['description']}\n"

        # Add product details if viewing a specific product
        if context.get('product_details'):
            prompt += f"\n\n=== CURRENTLY VIEWING PRODUCT ===\n"
            prompt += json.dumps(context['product_details'], indent=2) + "\n"

        # Add configuration validation if present
        if context.get('configuration_validation'):
            prompt += f"\n\n=== CONFIGURATION VALIDATION ===\n"
            prompt += json.dumps(context['configuration_validation'], indent=2) + "\n"

        return prompt

    def _determine_action_type(self, content: str, context: Dict) -> str:
        """Determine the type of action from the response"""
        content_lower = content.lower()

        if any(word in content_lower for word in ['recommend', 'suggest', 'try', 'consider']):
            return 'recommend'
        elif any(word in content_lower for word in ['customize', 'configure', 'select', 'choose']):
            return 'configure'
        else:
            return 'info'

    def _generate_fallback_response(self, user_message: str, context: Dict) -> Dict:
        """Generate fallback response using keyword matching"""
        message_lower = user_message.lower()

        # Simple keyword-based responses for gift shop
        if any(word in message_lower for word in ['explosion', 'box', 'boyfriend', 'girlfriend', 'surprise']):
            content = ("Great! Explosion boxes are perfect for creating memorable surprises! "
                      "These multi-layered boxes 'explode' with personalized notes, photos, and treats. "
                      "They're ideal for birthdays, anniversaries, or romantic gestures. "
                      "Would you like to see our explosion box options?")
            action_type = "recommend"

        elif any(word in message_lower for word in ['balloon', 'bouquet', 'celebration', 'party']):
            content = ("Excellent choice! Our balloon bouquets are perfect for celebrations! "
                      "We offer large arrangements with chocolates or gifts in the base. "
                      "Options include bubble balloons, heart foil bouquets, and custom designs. "
                      "Would you like to see what's available?")
            action_type = "recommend"

        elif any(word in message_lower for word in ['personalized', 'engraved', 'custom', 'executive', 'corporate']):
            content = ("Wonderful! Personalized gifts make lasting impressions. "
                      "We offer custom-engraved water bottles, premium leather wallets, and executive gift sets. "
                      "Perfect for corporate gifts, graduations, or special occasions. "
                      "What type of personalized item are you looking for?")
            action_type = "recommend"

        elif any(word in message_lower for word in ['birthday', 'anniversary', 'valentine', 'romantic']):
            content = ("Perfect! We have amazing gift options for special occasions! "
                      "Our explosion boxes and balloon bouquets are particularly popular for birthdays and anniversaries. "
                      "Would you like recommendations for a specific occasion?")
            action_type = "recommend"

        elif any(word in message_lower for word in ['chocolate', 'sweet', 'candy', 'treat']):
            content = ("Sweet choices! We offer various chocolate and candy options as fillers for our gifts. "
                      "Options include KitKat & Chocolates, Snickers & Mars Mix, and Mixed Sweets. "
                      "These can be added to explosion boxes or balloon bouquets. Would you like to see the options?")
            action_type = "recommend"

        elif any(word in message_lower for word in ['money', 'cash', 'display', 'ugx']):
            content = ("Interesting! We offer decorative money display services where we beautifully arrange "
                      "and fold cash for presentation in explosion boxes. "
                      "The service fee covers the creative folding and arrangement (actual money not included). "
                      "Would you like to know more about this option?")
            action_type = "info"

        elif any(word in message_lower for word in ['price', 'cost', 'cheap', 'affordable', 'budget']):
            content = ("I understand budget is important! Our gifts range from affordable options to premium sets. "
                      "We also offer installment payment plans with minimum upfront payments. "
                      "What's your budget range, and I'll recommend the best options?")
            action_type = "info"

        elif any(word in message_lower for word in ['customize', 'custom', 'build', 'create']):
            content = ("I'd love to help you create a custom gift! You can personalize explosion boxes, "
                      "balloon bouquets, or gift sets with various options. "
                      "Each choice affects the final look and price. Shall we start by selecting a gift type?")
            action_type = "configure"

        elif any(word in message_lower for word in ['shipping', 'delivery', 'ship']):
            content = ("We offer flexible shipping options throughout Kampala and Uganda! "
                      "Shipping costs depend on your location, product size, and delivery urgency. "
                      "During checkout, you'll see all available options. Need help with delivery arrangements?")
            action_type = "info"

        elif any(word in message_lower for word in ['payment', 'pay', 'installment', 'deposit']):
            content = ("We offer flexible payment options! You can pay in full or use our installment plan. "
                      "Some items have minimum upfront payment requirements (typically 20-50% depending on the item). "
                      "Would you like to know more about payment options?")
            action_type = "info"

        elif any(word in message_lower for word in ['gift', 'present', 'surprise', 'what', 'help']):
            content = ("I can help you find the perfect gift! Tell me a bit more:\n"
                      "• Who is it for? (partner, friend, boss, etc.)\n"
                      "• What's the occasion? (birthday, anniversary, thank you, etc.)\n"
                      "• What's your budget range?\n\n"
                      "This will help me recommend the best options for you!")
            action_type = "info"

        else:
            content = (f"Thanks for your question! I'm your AI assistant for Marcus Gift Shop. "
                      f"I can help you:\n\n"
                      f"• Find the perfect personalized gift\n"
                      f"• Customize explosion boxes and balloon bouquets\n"
                      f"• Explain product features and options\n"
                      f"• Provide pricing and budget guidance\n"
                      f"• Answer questions about shipping and payments\n\n"
                      f"What would you like help with today?")
            action_type = "info"

        return {
            "content": content,
            "metadata": {
                "actionType": action_type,
                "model": "keyword-fallback",
                "source": "fallback"
            }
        }

    def generate_product_recommendations(
        self,
        query: str,
        category_id: Optional[int] = None,
        price_max: Optional[float] = None,
        available_products: List[Dict] = None
    ) -> Dict:
        """
        Generate product recommendations based on query and filters.

        Args:
            query: User's search query
            category_id: Optional category filter
            price_max: Optional maximum price filter
            available_products: List of available products to recommend from

        Returns:
            Dictionary with recommended product IDs and explanation
        """
        if not available_products:
            return {
                "recommended_products": [],
                "explanation": "No products available at this time."
            }

        # Simple filtering based on query keywords
        query_lower = query.lower()
        recommendations = []

        for product in available_products[:5]:  # Top 5 recommendations
            product_name = product.get('name', '').lower()
            product_desc = product.get('description', '').lower()

            # Simple keyword matching
            if any(word in product_name or word in product_desc
                   for word in query_lower.split()):
                recommendations.append(product['id'])

        if not recommendations and available_products:
            # If no matches, return popular products
            recommendations = [p['id'] for p in available_products[:3]]

        explanation = f"Based on your interest in '{query}', I recommend these products."

        return {
            "recommended_products": recommendations,
            "explanation": explanation
        }


# Global instance
llm_service = LLMService()
