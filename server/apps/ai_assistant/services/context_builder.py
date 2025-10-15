"""
Context Builder Service
Gathers relevant product, category, and configuration information for AI responses
"""

from typing import Dict, List, Optional
from django.db import models
from apps.products.models import Category, Part, PartOption
from apps.preconfigured_products.models import PreConfiguredProduct
from apps.configurator.models import IncompatibilityRule, PriceAdjustmentRule


class ContextBuilder:
    """
    Builds enriched context for AI responses by fetching relevant
    database information based on session context.
    """

    @staticmethod
    def build_product_context(product_id: int) -> Dict:
        """Get detailed information about a specific product"""
        try:
            product = PreConfiguredProduct.objects.select_related('category').get(id=product_id)

            return {
                "product_id": product.id,
                "product_name": product.name,
                "category": product.category.name,
                "base_price": float(product.base_price),
                "description": product.description,
                "parts": [
                    {
                        "part_name": pp.part_option.part.name,
                        "option_name": pp.part_option.name,
                        "price": float(pp.part_option.default_price)
                    }
                    for pp in product.parts.select_related('part_option__part').all()
                ]
            }
        except PreConfiguredProduct.DoesNotExist:
            return {}

    @staticmethod
    def build_category_context(category_id: int) -> Dict:
        """Get information about a category and its parts"""
        try:
            category = Category.objects.get(id=category_id)
            parts = Part.objects.filter(category=category).prefetch_related('options')

            return {
                "category_id": category.id,
                "category_name": category.name,
                "description": category.description,
                "parts": [
                    {
                        "part_name": part.name,
                        "step": part.step,
                        "options_count": part.options.count()
                    }
                    for part in parts
                ]
            }
        except Category.DoesNotExist:
            return {}

    @staticmethod
    def get_top_products(category_id: Optional[int] = None, limit: int = 5) -> List[Dict]:
        """Get top products, optionally filtered by category"""
        query = PreConfiguredProduct.objects.select_related('category')

        if category_id:
            query = query.filter(category_id=category_id)

        products = query[:limit]

        return [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category.name,
                "base_price": float(p.base_price),
                "description": p.description
            }
            for p in products
        ]

    @staticmethod
    def get_categories() -> List[Dict]:
        """Get all available categories"""
        categories = Category.objects.all()

        return [
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description
            }
            for cat in categories
        ]

    @staticmethod
    def validate_configuration(category_id: int, configuration: Dict) -> Dict:
        """
        Validate a product configuration and provide suggestions.

        Args:
            category_id: The category ID
            configuration: Dict mapping part names to option IDs

        Returns:
            Dict with validation results and suggestions
        """
        issues = []
        suggestions = []

        # Get incompatibility rules
        option_ids = [int(option_id) for option_id in configuration.values() if option_id]

        if not option_ids:
            return {
                "is_valid": True,
                "issues": [],
                "suggestions": ["Start by selecting a frame type"]
            }

        # Check for incompatibilities
        incompatibilities = IncompatibilityRule.objects.filter(
            part_option__in=option_ids,
            incompatible_with_option__in=option_ids
        )

        for rule in incompatibilities:
            issues.append({
                "type": "incompatibility",
                "message": rule.message
            })

        # Get price adjustments (opportunities to save or upgrade)
        price_adjustments = PriceAdjustmentRule.objects.filter(
            condition_option__in=option_ids
        )

        for rule in price_adjustments:
            if rule.adjusted_price < 0:
                suggestions.append({
                    "type": "discount",
                    "message": f"You're getting a discount on this combination!"
                })
            elif rule.adjusted_price > 0:
                suggestions.append({
                    "type": "premium",
                    "message": f"This premium combination adds ${rule.adjusted_price}"
                })

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions if suggestions else ["Configuration looks good!"]
        }

    @staticmethod
    def get_part_options(part_name: str, category_id: int) -> List[Dict]:
        """Get available options for a specific part"""
        try:
            part = Part.objects.get(name=part_name, category_id=category_id)
            options = PartOption.objects.filter(part=part).select_related('part')

            return [
                {
                    "id": opt.id,
                    "name": opt.name,
                    "price": float(opt.default_price),
                    "description": opt.description
                }
                for opt in options
            ]
        except Part.DoesNotExist:
            return []

    @staticmethod
    def get_all_products_with_prices() -> List[Dict]:
        """
        Get all preconfigured products with their pricing.
        NOTE: base_price is the TOTAL price (already includes all parts).
        """
        products = PreConfiguredProduct.objects.select_related('category').prefetch_related(
            'parts__part_option__part'
        ).all()

        result = []
        for p in products:
            parts_list = []

            for pp in p.parts.all():
                parts_list.append({
                    "part": pp.part_option.part.name,
                    "option": pp.part_option.name,
                    "price": float(pp.part_option.default_price)
                })

            result.append({
                "id": p.id,
                "name": p.name,
                "category": p.category.name,
                "total_price": float(p.base_price),  # This is the FINAL price
                "parts": parts_list,
                "description": p.description or ""
            })

        return result

    @staticmethod
    def _is_option_compatible(option_id: int, selected_option_ids: List[int]) -> bool:
        """
        Check if an option is compatible with already selected options.
        Returns True if compatible, False if incompatible.
        """
        from apps.configurator.models import IncompatibilityRule

        if not selected_option_ids:
            return True

        # Check if this option has incompatibility rules with any selected options
        incompatibilities = IncompatibilityRule.objects.filter(
            models.Q(part_option_id=option_id, incompatible_with_option_id__in=selected_option_ids) |
            models.Q(part_option_id__in=selected_option_ids, incompatible_with_option_id=option_id)
        )

        return not incompatibilities.exists()

    @staticmethod
    def _calculate_option_price_with_adjustments(
        option: PartOption,
        selected_option_ids: List[int]
    ) -> float:
        """
        Calculate the actual price of an option considering price adjustment rules
        based on previously selected options.
        """
        from apps.configurator.models import PriceAdjustmentRule

        base_price = float(option.default_price)

        if not selected_option_ids:
            return base_price

        # Check if any selected option affects this option's price
        adjustment_rule = PriceAdjustmentRule.objects.filter(
            affected_option_id=option.id,
            condition_option_id__in=selected_option_ids
        ).first()

        if adjustment_rule:
            return base_price + float(adjustment_rule.adjusted_price)

        return base_price

    @staticmethod
    def calculate_cheapest_configurations() -> Dict[str, Dict]:
        """
        Calculate the absolute cheapest custom configuration for each category
        by selecting the cheapest compatible option for each part in order,
        respecting incompatibility and price adjustment rules.
        """
        categories = Category.objects.all()
        cheapest_configs = {}

        for category in categories:
            parts = Part.objects.filter(category=category).prefetch_related('options').order_by('step')

            if not parts:
                continue

            config = {
                "category": category.name,
                "category_id": category.id,
                "parts": [],
                "total_cost": 0.0,
                "selected_option_ids": []
            }

            # Build configuration iteratively, respecting rules
            for part in parts:
                cheapest_option = None
                cheapest_price = float('inf')

                # Try each option and find the cheapest compatible one
                for option in part.options.all():
                    # Check compatibility with already selected options
                    if not ContextBuilder._is_option_compatible(option.id, config["selected_option_ids"]):
                        continue

                    # Calculate price with adjustments
                    actual_price = ContextBuilder._calculate_option_price_with_adjustments(
                        option,
                        config["selected_option_ids"]
                    )

                    # Keep track of cheapest compatible option
                    if actual_price < cheapest_price:
                        cheapest_price = actual_price
                        cheapest_option = option

                # Add the cheapest compatible option
                if cheapest_option:
                    config["parts"].append({
                        "part": part.name,
                        "option": cheapest_option.name,
                        "price": cheapest_price
                    })
                    config["total_cost"] += cheapest_price
                    config["selected_option_ids"].append(cheapest_option.id)

            # Remove internal tracking field before returning
            del config["selected_option_ids"]
            cheapest_configs[category.name] = config

        return cheapest_configs

    @staticmethod
    def calculate_most_expensive_configurations() -> Dict[str, Dict]:
        """
        Calculate the most expensive custom configuration for each category
        by selecting the most expensive compatible option for each part in order,
        respecting incompatibility and price adjustment rules.
        """
        categories = Category.objects.all()
        expensive_configs = {}

        for category in categories:
            parts = Part.objects.filter(category=category).prefetch_related('options').order_by('step')

            if not parts:
                continue

            config = {
                "category": category.name,
                "category_id": category.id,
                "parts": [],
                "total_cost": 0.0,
                "selected_option_ids": []
            }

            # Build configuration iteratively, respecting rules
            for part in parts:
                most_expensive_option = None
                highest_price = float('-inf')

                # Try each option and find the most expensive compatible one
                for option in part.options.all():
                    # Check compatibility with already selected options
                    if not ContextBuilder._is_option_compatible(option.id, config["selected_option_ids"]):
                        continue

                    # Calculate price with adjustments
                    actual_price = ContextBuilder._calculate_option_price_with_adjustments(
                        option,
                        config["selected_option_ids"]
                    )

                    # Keep track of most expensive compatible option
                    if actual_price > highest_price:
                        highest_price = actual_price
                        most_expensive_option = option

                # Add the most expensive compatible option
                if most_expensive_option:
                    config["parts"].append({
                        "part": part.name,
                        "option": most_expensive_option.name,
                        "price": highest_price
                    })
                    config["total_cost"] += highest_price
                    config["selected_option_ids"].append(most_expensive_option.id)

            # Remove internal tracking field before returning
            del config["selected_option_ids"]
            expensive_configs[category.name] = config

        return expensive_configs

    @staticmethod
    def get_configuration_rules() -> Dict:
        """
        Get all incompatibility and price adjustment rules.
        This helps the LLM understand why certain configurations are/aren't possible.
        """
        from apps.configurator.models import IncompatibilityRule, PriceAdjustmentRule

        # Get incompatibility rules
        incompatibility_rules = []
        for rule in IncompatibilityRule.objects.select_related(
            'part_option__part',
            'incompatible_with_option__part'
        ).all():
            incompatibility_rules.append({
                "option1": f"{rule.part_option.part.name}: {rule.part_option.name}",
                "option2": f"{rule.incompatible_with_option.part.name}: {rule.incompatible_with_option.name}",
                "message": rule.message
            })

        # Get price adjustment rules
        price_adjustment_rules = []
        for rule in PriceAdjustmentRule.objects.select_related(
            'condition_option__part',
            'affected_option__part'
        ).all():
            price_adjustment_rules.append({
                "when_selected": f"{rule.condition_option.part.name}: {rule.condition_option.name}",
                "affects": f"{rule.affected_option.part.name}: {rule.affected_option.name}",
                "adjustment": float(rule.adjusted_price),
                "type": "discount" if float(rule.adjusted_price) < 0 else "premium"
            })

        return {
            "incompatibility_rules": incompatibility_rules,
            "price_adjustment_rules": price_adjustment_rules
        }

    @staticmethod
    def get_category_parts_and_options(category_id: Optional[int] = None) -> Dict:
        """Get all parts and their options for categories"""
        categories = Category.objects.all()
        if category_id:
            categories = categories.filter(id=category_id)

        result = {}
        for category in categories:
            parts = Part.objects.filter(category=category).prefetch_related('options')

            category_data = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "parts": []
            }

            for part in parts:
                options = []
                for opt in part.options.all():
                    # Check stock availability
                    try:
                        from apps.products.models import Stock
                        in_stock = Stock.objects.filter(part_option=opt, quantity__gt=0).exists()
                    except Exception:
                        in_stock = True  # Assume in stock if we can't check

                    options.append({
                        "id": opt.id,
                        "name": opt.name,
                        "price": float(opt.default_price),
                        "description": opt.description or "",
                        "in_stock": in_stock
                    })

                category_data["parts"].append({
                    "name": part.name,
                    "step": part.step,
                    "options": options
                })

            result[category.name] = category_data

        return result

    @staticmethod
    def build_enriched_context(session_context: Dict) -> Dict:
        """
        Build enriched context with database information.

        Args:
            session_context: The basic session context from frontend

        Returns:
            Enriched context dictionary
        """
        enriched = session_context.copy()

        # Add product details if viewing a product
        if session_context.get('productId'):
            product_context = ContextBuilder.build_product_context(
                int(session_context['productId'])
            )
            enriched['product_details'] = product_context

        # Add category details if in a category
        if session_context.get('categoryId'):
            category_context = ContextBuilder.build_category_context(
                int(session_context['categoryId'])
            )
            enriched['category_details'] = category_context

        # Validate configuration if present
        if session_context.get('configuration') and session_context.get('categoryId'):
            validation = ContextBuilder.validate_configuration(
                int(session_context['categoryId']),
                session_context['configuration']
            )
            enriched['configuration_validation'] = validation

        # Add available categories
        enriched['available_categories'] = ContextBuilder.get_categories()

        # Add preconfigured products (these are pre-built by admin)
        enriched['preconfigured_products'] = ContextBuilder.get_all_products_with_prices()

        # Add all parts and options for all categories (for custom configuration)
        enriched['category_parts'] = ContextBuilder.get_category_parts_and_options()

        # Calculate cheapest and most expensive CUSTOM configurations
        enriched['cheapest_custom_configs'] = ContextBuilder.calculate_cheapest_configurations()
        enriched['most_expensive_custom_configs'] = ContextBuilder.calculate_most_expensive_configurations()

        # Add configuration rules (incompatibility and price adjustments)
        enriched['configuration_rules'] = ContextBuilder.get_configuration_rules()

        return enriched


# Global instance
context_builder = ContextBuilder()
