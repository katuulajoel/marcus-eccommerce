"""
RAG (Retrieval Augmented Generation) Service
Retrieves relevant information from the product catalog to enhance AI responses
"""

from typing import List, Dict, Optional
from django.db.models import Q
from apps.products.models import Category, PartOption
from apps.preconfigured_products.models import PreConfiguredProduct


class RAGService:
    # Category keyword mapping for better matching
    CATEGORY_KEYWORDS = {
        "Explosion Boxes": [
            "explosion boxes", "explosion box", "exploding box", "exploding boxes",
            "surprise box", "surprise boxes", "memory box", "memory boxes"
        ],
        "Balloon Bouquets": [
            "balloon bouquets", "balloon bouquet", "balloons", "balloon",
            "balloon arrangement", "balloon arrangements"
        ],
        "Personalized Sets": [
            "personalized sets", "personalized set", "personalised sets", "personalised set",
            "custom set", "custom sets", "engraved set", "engraved sets",
            "personalized gift", "personalised gift"
        ]
    }
    """
    Simple RAG service using text-based search.
    This can be upgraded to use vector embeddings once pgvector is available.
    """

    @staticmethod
    def search_products(query: str, category_id: Optional[int] = None, limit: int = 5) -> List[Dict]:
        """
        Search for products based on text query.

        Args:
            query: Search query from user
            category_id: Optional category filter
            limit: Maximum number of results

        Returns:
            List of matching products with relevance scores
        """
        # Build query
        products = PreConfiguredProduct.objects.select_related('category')

        if category_id:
            products = products.filter(category_id=category_id)

        # Simple text search in name and description
        query_terms = query.lower().split()
        q_objects = Q()

        for term in query_terms:
            q_objects |= Q(name__icontains=term) | Q(description__icontains=term)

        products = products.filter(q_objects).distinct()[:limit]

        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category.name,
                "category_id": p.category.id,
                "base_price": float(p.base_price),
                "description": p.description or "",
                "image_url": p.image.url if p.image else None,
                "relevance_score": RAGService._calculate_relevance(p, query_terms)
            }
            for p in products
        ]

    @staticmethod
    def _calculate_relevance(product, query_terms: List[str]) -> float:
        """Calculate simple relevance score based on keyword matches"""
        score = 0.0
        name_lower = product.name.lower()
        desc_lower = (product.description or "").lower()

        for term in query_terms:
            if term in name_lower:
                score += 2.0  # Higher weight for name matches
            if term in desc_lower:
                score += 1.0  # Lower weight for description matches

        return score

    @staticmethod
    def search_part_options(query: str, category_id: Optional[int] = None, limit: int = 5) -> List[Dict]:
        """
        Search for part options based on query.

        Args:
            query: Search query
            category_id: Optional category filter
            limit: Maximum results

        Returns:
            List of matching part options
        """
        options = PartOption.objects.select_related('part', 'part__category')

        if category_id:
            options = options.filter(part__category_id=category_id)

        query_terms = query.lower().split()
        q_objects = Q()

        for term in query_terms:
            q_objects |= Q(name__icontains=term) | Q(description__icontains=term)

        options = options.filter(q_objects).distinct()[:limit]

        return [
            {
                "id": opt.id,
                "name": opt.name,
                "part_name": opt.part.name,
                "category": opt.part.category.name,
                "price": float(opt.default_price),
                "description": opt.description or "",
                "image_url": opt.image.url if opt.image else None
            }
            for opt in options
        ]

    @staticmethod
    def get_similar_products(product_id: int, limit: int = 3) -> List[Dict]:
        """
        Find similar products based on category and price range.

        Args:
            product_id: Reference product ID
            limit: Maximum results

        Returns:
            List of similar products
        """
        try:
            product = PreConfiguredProduct.objects.get(id=product_id)

            # Find products in same category with similar price
            price_min = float(product.base_price) * 0.7
            price_max = float(product.base_price) * 1.3

            similar = PreConfiguredProduct.objects.filter(
                category=product.category,
                base_price__gte=price_min,
                base_price__lte=price_max
            ).exclude(id=product_id).select_related('category')[:limit]

            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "category": p.category.name,
                    "base_price": float(p.base_price),
                    "description": p.description or "",
                    "image_url": p.image.url if p.image else None
                }
                for p in similar
            ]
        except PreConfiguredProduct.DoesNotExist:
            return []

    @staticmethod
    def get_products_by_category(category_name: str, limit: int = 5) -> List[Dict]:
        """Get products for a specific category by name"""
        try:
            category = Category.objects.get(name__iexact=category_name)

            products = PreConfiguredProduct.objects.filter(
                category=category
            ).select_related('category')[:limit]

            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "category": p.category.name,
                    "category_id": p.category.id,
                    "base_price": float(p.base_price),
                    "description": p.description or "",
                    "image_url": p.image.url if p.image else None
                }
                for p in products
            ]
        except Category.DoesNotExist:
            return []

    @staticmethod
    def get_products_by_price_range(
        min_price: float,
        max_price: float,
        category_id: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Get products within a specific price range"""
        products = PreConfiguredProduct.objects.filter(
            base_price__gte=min_price,
            base_price__lte=max_price
        ).select_related('category')

        if category_id:
            products = products.filter(category_id=category_id)

        products = products[:limit]

        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category.name,
                "category_id": p.category.id,
                "base_price": float(p.base_price),
                "description": p.description or "",
                "image_url": p.image.url if p.image else None
            }
            for p in products
        ]

    @staticmethod
    def retrieve_context_for_query(query: str, session_context: Dict) -> Dict:
        """
        Retrieve relevant context for a user query.
        This is the main RAG retrieval method.

        Args:
            query: User's query
            session_context: Current session context

        Returns:
            Dictionary with retrieved products, parts, and relevant information
        """
        query_lower = query.lower()
        category_id = session_context.get('categoryId')

        # Detect intent from query
        intent = RAGService._detect_intent(query_lower)

        context = {
            "intent": intent,
            "products": [],
            "part_options": [],
            "categories": []
        }

        # Search based on intent
        if intent == "product_search":
            context["products"] = RAGService.search_products(query, category_id)

            # Fallback if no products found
            if not context["products"]:
                context["search_fallback"] = True
                # Try showing products from relevant category
                if category_id:
                    try:
                        from apps.products.models import Category
                        category = Category.objects.get(id=category_id)
                        context["products"] = RAGService.get_products_by_category(category.name, limit=3)
                    except Exception:
                        pass

                # If still empty, show popular products
                if not context["products"]:
                    from apps.preconfigured_products.models import PreConfiguredProduct
                    products = PreConfiguredProduct.objects.select_related('category').order_by('-id')[:5]
                    context["products"] = [
                        {
                            "id": p.id,
                            "name": p.name,
                            "category": p.category.name,
                            "category_id": p.category.id,
                            "base_price": float(p.base_price),
                            "description": p.description or "",
                            "image_url": p.image.url if p.image else None
                        }
                        for p in products
                    ]

        elif intent == "category_browse":
            # Extract category name using improved matching
            category_name = RAGService._extract_category_from_query(query_lower)
            if category_name:
                context["products"] = RAGService.get_products_by_category(category_name)

        elif intent == "price_inquiry":
            # Try to extract price from query - handle comma-separated numbers
            import re
            price_match = re.search(r'\$?([\d,]+)', query)
            if price_match:
                # Remove commas and convert to float
                price_str = price_match.group(1).replace(',', '')
                max_price = float(price_str)
                context["products"] = RAGService.get_products_by_price_range(
                    0, max_price, category_id
                )

        elif intent == "part_search":
            context["part_options"] = RAGService.search_part_options(query, category_id)

        elif intent == "comparison":
            # Get products for comparison
            context["products"] = RAGService.search_products(query, category_id, limit=3)

        elif intent == "customization":
            # For customization queries, retrieve part options but not products
            context["part_options"] = RAGService.search_part_options(query, category_id)

        elif intent == "info_only":
            # For informational queries, don't retrieve any products
            # Just return the intent so LLM can answer the question
            pass

        elif intent == "general":
            # For general queries, don't automatically show products
            # Let the LLM decide if recommendations are needed based on context
            pass

        return context

    @staticmethod
    def _extract_category_from_query(query_lower: str):
        """Extract category name from query using keyword matching"""
        # Sort keywords by length (longest first) to match specific phrases first
        all_keywords = []
        for category, keywords in RAGService.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                all_keywords.append((keyword, category))

        all_keywords.sort(key=lambda x: len(x[0]), reverse=True)

        for keyword, category in all_keywords:
            if keyword in query_lower:
                return category

        return None

    @staticmethod
    def _detect_intent(query_lower: str) -> str:
        """Detect user intent from query - prioritize specific intents over general ones"""

        # Check for specific product requests first (highest priority)
        product_request_keywords = [
            "show", "find", "looking for", "need", "want",
            "get me", "i'd like", "interested in", "searching for",
            "do you have", "got any", "recommend", "suggest",
            "gift for", "present for", "something for", "ideas for"
        ]
        if any(word in query_lower for word in product_request_keywords):
            return "product_search"

        # Check for category mentions
        if any(word in query_lower for word in ["explosion", "balloon", "personalized", "category", "boxes", "bouquets", "sets"]):
            return "category_browse"

        # Check for comparison requests
        if any(word in query_lower for word in ["compare", "difference", "vs", "versus"]):
            return "comparison"

        # Check for part/customization options
        if any(word in query_lower for word in ["filler", "chocolate", "balloon style", "engraved", "part", "option"]):
            return "part_search"

        # Price inquiry (lower priority - check if there are gift-related keywords)
        if any(word in query_lower for word in ["price", "cost", "budget", "afford", "cheap", "ugx"]):
            # Check if there are also product/gift-related keywords - prioritize product search
            gift_keywords = [
                # Recipients
                "boyfriend", "girlfriend", "husband", "wife", "partner", "spouse",
                "mom", "mum", "mother", "dad", "father", "parents",
                "sister", "brother", "friend", "boss", "colleague", "coworker",
                "grandma", "grandpa", "aunt", "uncle", "cousin",
                # Occasions
                "birthday", "anniversary", "valentine", "valentines",
                "wedding", "engagement", "graduation", "promotion",
                "christmas", "xmas", "mother's day", "father's day",
                "thank you", "thanks", "apology", "congratulations", "congrats",
                "baby shower", "farewell",
                # General
                "gift", "surprise", "present", "for"
            ]
            if any(word in query_lower for word in gift_keywords):
                return "product_search"
            return "price_inquiry"

        # Customization requests (without product search intent)
        if any(word in query_lower for word in ["customize", "build", "create", "personalize"]):
            return "customization"

        # Informational queries - no product recommendations needed
        if any(word in query_lower for word in [
            "how to", "how do", "what is", "explain", "tell me about",
            "shipping", "delivery", "payment", "installment",
            "return", "refund", "policy", "contact", "help"
        ]):
            return "info_only"

        # Default to general
        return "general"

    @staticmethod
    def should_include_products(intent: str) -> bool:
        """
        Determine if products should be included in the response based on intent.

        Returns:
            True if products should be retrieved and shown, False otherwise
        """
        # Only include products for intents where recommendations are explicitly useful
        recommendation_intents = {
            "product_search",      # User explicitly looking for products
            "category_browse",     # Browsing a category
            "comparison",          # Comparing products
            "price_inquiry",       # Looking for products in price range
        }

        return intent in recommendation_intents


# Global instance
rag_service = RAGService()
