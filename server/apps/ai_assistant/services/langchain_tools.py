"""
LangChain Tools for Marcus E-commerce
These tools allow the LangChain agent to interact with the e-commerce platform.
Tools are dynamically powered by Django models - no hardcoding!
"""

from typing import Optional, List, Dict
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from .index_service import get_index_service
from .context_builder import context_builder


# Tool Input Schemas
class SearchProductsInput(BaseModel):
    """Input for searching products"""
    query: str = Field(description="Natural language search query for products")
    category_id: Optional[int] = Field(default=None, description="Optional category ID to filter results")


class SearchCategoriesInput(BaseModel):
    """Input for searching categories"""
    query: str = Field(description="Natural language search query for categories")


class ValidateConfigurationInput(BaseModel):
    """Input for validating product configuration"""
    category_id: int = Field(description="Category ID for the product being configured")
    configuration: Dict[str, str] = Field(description="Dictionary mapping part names to option IDs")


class CalculatePriceInput(BaseModel):
    """Input for calculating product price"""
    category_id: int = Field(description="Category ID")
    configuration: Dict[str, str] = Field(description="Dictionary mapping part names to option IDs")


class GetPartOptionsInput(BaseModel):
    """Input for getting part options"""
    part_name: str = Field(description="Name of the part (e.g., 'Frame', 'Wheels')")
    category_id: int = Field(description="Category ID")


class GetAvailableCategoriesInput(BaseModel):
    """Input for getting available categories"""
    pass  # No input needed


# LangChain Tools
class SearchProductsTool(BaseTool):
    """
    Search for products using semantic search.
    Powered by LlamaIndex - automatically searches all products in database.
    """
    name: str = "search_products"
    description: str = """
    Search for products based on natural language query.
    Use this when user asks about specific products, wants recommendations,
    or is looking for products with certain features.

    Example queries:
    - "I need a mountain bike"
    - "Show me beginner-friendly bikes"
    - "What's your cheapest bike?"
    - "I want something for trail riding"

    Returns list of matching products with prices and descriptions.
    """
    args_schema: type[BaseModel] = SearchProductsInput

    def _run(self, query: str, category_id: Optional[int] = None) -> str:
        """Execute the search"""
        index_service = get_index_service()
        products = index_service.search_products(query, category_id)

        if not products:
            return f"No products found matching '{query}'. Try a different search."

        # Format results
        result = f"Found {len(products)} matching products:\n\n"
        for i, product in enumerate(products[:5], 1):  # Top 5
            result += f"{i}. {product['name']}\n"
            result += f"   Category: {product['category']}\n"
            result += f"   Price: ${product['base_price']}\n"
            result += f"   Relevance: {product['relevance_score']:.2f}\n\n"

        return result

    def _arun(self, query: str, category_id: Optional[int] = None):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


class SearchCategoriesTool(BaseTool):
    """
    Search for product categories using semantic search.
    Dynamically discovers all categories from database.
    """
    name: str = "search_categories"
    description: str = """
    Search for product categories based on natural language query.
    Use this when user asks what types of products are available,
    or wants to browse categories.

    Example queries:
    - "What types of products do you sell?"
    - "Show me all categories"
    - "Do you have bikes?"

    Returns list of matching categories.
    """
    args_schema: type[BaseModel] = SearchCategoriesInput

    def _run(self, query: str) -> str:
        """Execute the search"""
        index_service = get_index_service()
        categories = index_service.search_categories(query)

        if not categories:
            # Fallback to context builder
            all_categories = context_builder.get_categories()
            result = "Available categories:\n\n"
            for cat in all_categories:
                result += f"- {cat['name']}: {cat['description']}\n"
            return result

        result = f"Found {len(categories)} matching categories:\n\n"
        for cat in categories:
            result += f"- {cat['name']} ({cat['parts_count']} customizable parts)\n"

        return result

    def _arun(self, query: str):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


class ValidateConfigurationTool(BaseTool):
    """
    Validate a product configuration for compatibility issues.
    Checks incompatibility rules from database.
    """
    name: str = "validate_configuration"
    description: str = """
    Validate if a product configuration is compatible.
    Use this when user has selected parts and you need to check
    if they work together, or when suggesting configurations.

    Checks:
    - Incompatibility between selected parts
    - Price adjustments (discounts/premiums)
    - Configuration completeness

    Returns validation results with issues and suggestions.
    """
    args_schema: type[BaseModel] = ValidateConfigurationInput

    def _run(self, category_id: int, configuration: Dict[str, str]) -> str:
        """Execute validation"""
        validation = context_builder.validate_configuration(category_id, configuration)

        result = ""
        if validation['is_valid']:
            result = "✓ Configuration is valid!\n\n"
        else:
            result = "✗ Configuration has issues:\n\n"
            for issue in validation['issues']:
                result += f"- {issue['message']}\n"
            result += "\n"

        if validation['suggestions']:
            result += "Suggestions:\n"
            for suggestion in validation['suggestions']:
                if isinstance(suggestion, dict):
                    result += f"- {suggestion.get('message', suggestion)}\n"
                else:
                    result += f"- {suggestion}\n"

        return result

    def _arun(self, category_id: int, configuration: Dict[str, str]):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


class GetPartOptionsTool(BaseTool):
    """
    Get available options for a specific part.
    Dynamically queries database for current inventory.
    """
    name: str = "get_part_options"
    description: str = """
    Get available options for a specific part type.
    Use this when user asks about customization options,
    wants to see what's available for a part, or needs pricing info.

    Example queries:
    - "What frame options are available?"
    - "Show me wheel choices"
    - "How much do different handlebars cost?"

    Returns list of options with prices and stock status.
    """
    args_schema: type[BaseModel] = GetPartOptionsInput

    def _run(self, part_name: str, category_id: int) -> str:
        """Get part options"""
        options = context_builder.get_part_options(part_name, category_id)

        if not options:
            return f"No options found for {part_name}. This part may not exist in the selected category."

        result = f"Available {part_name} options:\n\n"
        for option in options:
            stock = "✓ In Stock" if option.get('in_stock', True) else "✗ Out of Stock"
            result += f"- {option['name']}: ${option['price']} ({stock})\n"
            if option.get('description'):
                result += f"  {option['description']}\n"

        return result

    def _arun(self, part_name: str, category_id: int):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


class GetAvailableCategoriesTool(BaseTool):
    """
    Get all available product categories.
    Simple tool to list all categories without search.
    """
    name: str = "get_available_categories"
    description: str = """
    Get a complete list of all product categories available in the store.
    Use this for a straightforward category listing.

    Returns all categories with descriptions.
    """
    args_schema: type[BaseModel] = GetAvailableCategoriesInput

    def _run(self) -> str:
        """Get all categories"""
        categories = context_builder.get_categories()

        result = "Available product categories:\n\n"
        for cat in categories:
            result += f"- {cat['name']} (ID: {cat['id']})\n"
            if cat.get('description'):
                result += f"  {cat['description']}\n"
            result += "\n"

        return result

    def _arun(self):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


class GetPriceRangeTool(BaseTool):
    """
    Get price ranges for products in a category.
    Uses dynamically calculated min/max from database.
    """
    name: str = "get_price_range"
    description: str = """
    Get price range information for a category.
    Use this when user asks about budget, pricing, or cost ranges.

    Example queries:
    - "How much do bikes cost?"
    - "What's your price range?"
    - "Do you have anything under $500?"

    Returns cheapest and most expensive configurations.
    """
    args_schema: type[BaseModel] = SearchCategoriesInput  # Reuse this schema

    def _run(self, query: str) -> str:
        """Get price ranges"""
        # Get cheapest and most expensive configs
        cheapest = context_builder.calculate_cheapest_configurations()
        expensive = context_builder.calculate_most_expensive_configurations()

        # Try to match query to category
        index_service = get_index_service()
        categories = index_service.search_categories(query)

        result = "Price Ranges:\n\n"

        if categories:
            # Show specific category
            cat_name = categories[0]['name']
            if cat_name in cheapest:
                result += f"{cat_name}:\n"
                result += f"  Cheapest: ${cheapest[cat_name]['total_cost']:.2f}\n"
                result += f"  Most Expensive: ${expensive[cat_name]['total_cost']:.2f}\n"
        else:
            # Show all categories
            for cat_name in cheapest.keys():
                result += f"{cat_name}:\n"
                result += f"  Cheapest: ${cheapest[cat_name]['total_cost']:.2f}\n"
                result += f"  Most Expensive: ${expensive[cat_name]['total_cost']:.2f}\n\n"

        return result

    def _arun(self, query: str):
        """Async version (not implemented)"""
        raise NotImplementedError("Async not supported")


# Export all tools
def get_all_tools() -> List[BaseTool]:
    """
    Get all available tools for the LangChain agent.
    These tools are dynamically powered by Django models!
    """
    return [
        SearchProductsTool(),
        SearchCategoriesTool(),
        ValidateConfigurationTool(),
        GetPartOptionsTool(),
        GetAvailableCategoriesTool(),
        GetPriceRangeTool()
    ]
