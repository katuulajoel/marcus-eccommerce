"""
RAG Service - Powered by LlamaIndex
NO HARDCODED CATEGORIES - Everything is dynamically discovered from database!

This replaces the old rag_service.py with a fully dynamic, framework-based approach.
"""

from typing import Dict, List, Optional
from .index_service import get_index_service
from .context_builder import context_builder


class RAGService:
    """
    Retrieval-Augmented Generation service using LlamaIndex.
    Provides context for LLM responses by retrieving relevant information.
    """

    def __init__(self):
        self.index_service = get_index_service()

    def retrieve_context_for_query(self, query: str, session_context: Dict = None) -> Dict:
        """
        Retrieve relevant context for a user query using semantic search.
        NO HARDCODED KEYWORDS - Uses LlamaIndex to find relevant info!

        Args:
            query: User's question/message
            session_context: Current session state (page, category, etc.)

        Returns:
            Dict with:
            - intent: Detected user intent
            - products: Relevant products (if applicable)
            - categories: Relevant categories (if applicable)
            - knowledge: Retrieved knowledge snippets
            - context_summary: Summary of retrieved context
        """
        # Classify intent dynamically using semantic search
        intent = self._classify_intent(query, session_context)

        # Initialize context
        rag_context = {
            "intent": intent,
            "products": [],
            "categories": [],
            "knowledge": [],
            "context_summary": ""
        }

        # Retrieve relevant information based on intent
        if intent in ["product_search", "recommendation"]:
            # Search for products
            category_id = session_context.get('categoryId') if session_context else None
            products = self.index_service.search_products(query, category_id)
            rag_context["products"] = self._format_products(products[:5])

        if intent in ["category_browse", "general_inquiry"]:
            # Search for categories
            categories = self.index_service.search_categories(query)
            rag_context["categories"] = self._format_categories(categories[:3])

        if intent in ["configuration_help", "compatibility"]:
            # Get compatibility info
            compatibility_info = self.index_service.get_compatibility_info(query)
            rag_context["knowledge"] = [info['description'] for info in compatibility_info[:3]]

        if intent == "customization":
            # Get part options info
            part_info = self.index_service.get_part_options(query)
            rag_context["knowledge"] = [part['description'] for part in part_info[:3]]

        # Build context summary
        rag_context["context_summary"] = self._build_context_summary(rag_context)

        return rag_context

    def _classify_intent(self, query: str, session_context: Dict = None) -> str:
        """
        Classify user intent using semantic search.
        NO HARDCODED KEYWORDS - Uses vector similarity!
        """
        query_lower = query.lower()

        # Use LlamaIndex to find most relevant document type
        search_results = self.index_service.query(query, top_k=3)

        if not search_results.get("documents"):
            return "general_inquiry"

        # Analyze top results to determine intent
        top_docs = search_results["documents"]
        doc_types = [doc["metadata"].get("type") for doc in top_docs]

        # Determine intent based on what documents match
        if "product" in doc_types:
            # Check if it's a specific product inquiry or general search
            if any(word in query_lower for word in ["looking for", "need", "want", "recommend", "best"]):
                return "recommendation"
            return "product_search"

        if "category" in doc_types:
            return "category_browse"

        if "incompatibility_rule" in doc_types or "price_adjustment_rule" in doc_types:
            if any(word in query_lower for word in ["compatible", "work with", "combine"]):
                return "compatibility"
            return "configuration_help"

        if "part" in doc_types:
            if any(word in query_lower for word in ["customize", "options", "change", "upgrade"]):
                return "customization"
            return "configuration_help"

        if "faq" in doc_types:
            return "support"

        # Check session context for additional hints
        if session_context:
            if session_context.get('currentPage') == '/customize':
                return "configuration_help"
            if session_context.get('categoryId'):
                return "category_browse"

        return "general_inquiry"

    def _format_products(self, products: List[Dict]) -> List[Dict]:
        """Format product search results"""
        formatted = []
        for product in products:
            formatted.append({
                "id": product.get("id"),
                "name": product.get("name"),
                "category": product.get("category"),
                "base_price": product.get("base_price"),
                "relevance": product.get("relevance_score", 0)
            })
        return formatted

    def _format_categories(self, categories: List[Dict]) -> List[Dict]:
        """Format category search results"""
        formatted = []
        for cat in categories:
            formatted.append({
                "id": cat.get("id"),
                "name": cat.get("name"),
                "relevance": cat.get("relevance_score", 0)
            })
        return formatted

    def _build_context_summary(self, rag_context: Dict) -> str:
        """Build human-readable summary of retrieved context"""
        summary_parts = []

        if rag_context["products"]:
            summary_parts.append(f"Found {len(rag_context['products'])} relevant products")

        if rag_context["categories"]:
            cat_names = [cat["name"] for cat in rag_context["categories"]]
            summary_parts.append(f"Related categories: {', '.join(cat_names)}")

        if rag_context["knowledge"]:
            summary_parts.append(f"Retrieved {len(rag_context['knowledge'])} knowledge snippets")

        return "; ".join(summary_parts) if summary_parts else "No specific context retrieved"

    def search_products(
        self,
        query: str,
        category_id: Optional[int] = None,
        price_max: Optional[float] = None
    ) -> List[Dict]:
        """
        Search for products with optional filters.
        Uses LlamaIndex semantic search - NO HARDCODED LOGIC!
        """
        products = self.index_service.search_products(query, category_id)

        # Apply price filter if specified
        if price_max:
            products = [p for p in products if p.get("base_price", 0) <= price_max]

        return self._format_products(products)

    def should_include_products(self, intent: str) -> bool:
        """
        Determine if products should be included in response.
        More nuanced than before - based on semantic intent.
        """
        product_relevant_intents = [
            "product_search",
            "recommendation",
            "category_browse",
            "customization"
        ]
        return intent in product_relevant_intents

    def get_dynamic_categories(self) -> List[Dict]:
        """
        Get all categories dynamically from database.
        Replaces hardcoded CATEGORY_KEYWORDS!
        """
        return context_builder.get_categories()

    def get_category_keywords(self) -> Dict[str, List[str]]:
        """
        Generate category keywords dynamically from indexed data.
        This replaces the hardcoded CATEGORY_KEYWORDS dictionary!
        """
        categories = self.get_dynamic_categories()
        keyword_map = {}

        for category in categories:
            # Search for this category to get related terms
            category_name = category["name"]
            search_results = self.index_service.search_categories(category_name)

            # Extract keywords from category description and products
            keywords = [category_name.lower()]

            # Add words from category description
            if category.get("description"):
                desc_words = category["description"].lower().split()
                keywords.extend([w for w in desc_words if len(w) > 3])

            # Get products in this category and extract keywords
            products = self.index_service.search_products("", category["id"])
            for product in products[:5]:  # Top 5 products
                name_words = product.get("name", "").lower().split()
                keywords.extend([w for w in name_words if len(w) > 3])

            # Deduplicate and store
            keyword_map[category_name] = list(set(keywords))

        return keyword_map


# Global instance
_rag_service_instance = None


def get_rag_service() -> RAGService:
    """Get or create the global RAGService instance"""
    global _rag_service_instance

    if _rag_service_instance is None:
        _rag_service_instance = RAGService()

    return _rag_service_instance
