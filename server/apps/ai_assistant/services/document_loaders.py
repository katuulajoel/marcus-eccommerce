"""
LlamaIndex Document Loaders for Django Models
Automatically converts Django database models into LlamaIndex documents for RAG
"""

from typing import List
from llama_index.core import Document
from apps.products.models import Category, Part, PartOption, Stock
from apps.preconfigured_products.models import PreConfiguredProduct
from apps.configurator.models import IncompatibilityRule, PriceAdjustmentRule
from apps.shipping.models import ShippingZone, ShippingRate, ShippingConstants, ZoneArea


class CategoryDocumentLoader:
    """
    Converts Category models into LlamaIndex documents.
    No hardcoded categories - discovers everything from database!
    """

    @staticmethod
    def load() -> List[Document]:
        """Load all categories as documents"""
        documents = []
        categories = Category.objects.all()

        for category in categories:
            # Get part count for this category
            parts_count = Part.objects.filter(category=category).count()

            # Build rich text content for embedding with shipping details
            shipping_info = ""
            if category.unit_weight_kg > 0:
                shipping_info = f"""
Shipping Profile:
- Dimensions: {category.unit_length_cm}cm x {category.unit_width_cm}cm x {category.unit_height_cm}cm
- Weight: {category.unit_weight_kg}kg per unit
- Stackable: {'Yes' if category.stackable else 'No'}
- Max quantity per boda boda: {category.max_boda_quantity}
- Requires delivery helper: {'Yes' if category.requires_helper else 'No'}
- Requires extra care handling: {'Yes' if category.requires_extra_care else 'No'}
- Shipping notes: {category.shipping_notes or 'None'}
"""

            content = f"""
Category: {category.name}
Description: {category.description or 'No description'}
Available Parts: {parts_count}
Category ID: {category.id}
{shipping_info}
This is a product category in Marcus Custom Bikes e-commerce platform.
Customers can browse and customize products in this category.
"""

            # Create document with metadata
            doc = Document(
                text=content,
                doc_id=f"category_{category.id}",  # Unique ID for updates
                metadata={
                    "type": "category",
                    "category_id": category.id,
                    "category_name": category.name,
                    "parts_count": parts_count
                }
            )
            documents.append(doc)

        return documents


class ProductDocumentLoader:
    """
    Converts PreConfiguredProduct models into LlamaIndex documents.
    These are pre-built products that customers can customize.
    """

    @staticmethod
    def load() -> List[Document]:
        """Load all preconfigured products as documents"""
        documents = []
        products = PreConfiguredProduct.objects.select_related('category').prefetch_related(
            'parts__part_option__part'
        ).all()

        for product in products:
            # Build detailed product description
            parts_description = []
            for pp in product.parts.all():
                parts_description.append(
                    f"- {pp.part_option.part.name}: {pp.part_option.name} (${pp.part_option.default_price})"
                )

            content = f"""
Product: {product.name}
Category: {product.category.name}
Base Price: ${product.base_price}
Description: {product.description or 'No description'}

Configuration:
{chr(10).join(parts_description)}

Product ID: {product.id}

This is a pre-configured {product.category.name.lower()} that customers can purchase as-is
or customize by changing individual parts. The base price includes all listed components.
"""

            doc = Document(
                text=content,
                doc_id=f"product_{product.id}",  # Unique ID for updates
                metadata={
                    "type": "product",
                    "product_id": product.id,
                    "product_name": product.name,
                    "category_id": product.category.id,
                    "category_name": product.category.name,
                    "base_price": float(product.base_price)
                }
            )
            documents.append(doc)

        return documents


class PartOptionDocumentLoader:
    """
    Converts Part and PartOption models into LlamaIndex documents.
    This helps the AI understand what customization options are available.
    """

    @staticmethod
    def load() -> List[Document]:
        """Load all part options as documents"""
        documents = []
        parts = Part.objects.select_related('category').prefetch_related('options').all()

        for part in parts:
            options_description = []
            for option in part.options.all():
                # Check stock
                in_stock = Stock.objects.filter(part_option=option, quantity__gt=0).exists()
                stock_status = "In Stock" if in_stock else "Out of Stock"

                options_description.append(
                    f"- {option.name}: ${option.default_price} ({stock_status})"
                )

            content = f"""
Part Type: {part.name}
Category: {part.category.name}
Configuration Step: {part.step}

Available Options:
{chr(10).join(options_description)}

This is a customizable part for {part.category.name.lower()}.
Customers must select one option from this part type when building their product.
"""

            doc = Document(
                text=content,
                doc_id=f"part_{part.id}",  # Unique ID for updates
                metadata={
                    "type": "part",
                    "part_name": part.name,
                    "category_id": part.category.id,
                    "category_name": part.category.name,
                    "step": part.step,
                    "options_count": part.options.count()
                }
            )
            documents.append(doc)

        return documents


class RulesDocumentLoader:
    """
    Converts IncompatibilityRule and PriceAdjustmentRule into documents.
    This teaches the AI about product configuration rules and pricing logic.
    """

    @staticmethod
    def load() -> List[Document]:
        """Load all compatibility and pricing rules as documents"""
        documents = []

        # Load incompatibility rules
        incompatibility_rules = IncompatibilityRule.objects.select_related(
            'part_option__part',
            'incompatible_with_option__part'
        ).all()

        for rule in incompatibility_rules:
            content = f"""
Incompatibility Rule:
{rule.part_option.part.name} "{rule.part_option.name}" is NOT compatible with
{rule.incompatible_with_option.part.name} "{rule.incompatible_with_option.name}"

Reason: {rule.message}

When a customer selects one of these options, the other option should not be available.
This is an important configuration constraint.
"""

            doc = Document(
                text=content,
                doc_id=f"incompatibility_rule_{rule.id}",  # Unique ID for updates
                metadata={
                    "type": "incompatibility_rule",
                    "rule_id": rule.id,
                    "option1_id": rule.part_option.id,
                    "option2_id": rule.incompatible_with_option.id,
                    "rule_message": rule.message
                }
            )
            documents.append(doc)

        # Load price adjustment rules
        price_rules = PriceAdjustmentRule.objects.select_related(
            'condition_option__part',
            'affected_option__part'
        ).all()

        for rule in price_rules:
            adjustment_type = "discount" if float(rule.adjusted_price) < 0 else "premium"
            amount = abs(float(rule.adjusted_price))

            content = f"""
Price Adjustment Rule:
When customer selects {rule.condition_option.part.name} "{rule.condition_option.name}",
the price of {rule.affected_option.part.name} "{rule.affected_option.name}"
gets a ${amount} {adjustment_type}.

This is a special pricing rule that affects the final product price.
"""

            doc = Document(
                text=content,
                doc_id=f"price_rule_{rule.id}",  # Unique ID for updates
                metadata={
                    "type": "price_adjustment_rule",
                    "rule_id": rule.id,
                    "condition_option_id": rule.condition_option.id,
                    "affected_option_id": rule.affected_option.id,
                    "adjustment_amount": float(rule.adjusted_price),
                    "adjustment_type": adjustment_type
                }
            )
            documents.append(doc)

        return documents


class ShippingDocumentLoader:
    """
    Converts shipping zones, rates, and constants into LlamaIndex documents.
    This teaches the AI about delivery options, costs, and logistics.
    """

    @staticmethod
    def load() -> List[Document]:
        """Load shipping information as documents"""
        documents = []

        # Load shipping constants
        try:
            constants = ShippingConstants.get_instance()
            content = f"""
Shipping System Configuration:

Boda Boda (Motorcycle) Limits:
- Maximum weight: {constants.boda_max_weight_kg}kg
- Maximum dimensions: {constants.boda_max_length_cm}cm x {constants.boda_max_width_cm}cm x {constants.boda_max_height_cm}cm
- Best for: Small, lightweight items within city limits

Van/Pickup Limits:
- Maximum weight: {constants.van_max_weight_kg}kg
- Maximum dimensions: {constants.van_max_length_cm}cm x {constants.van_max_width_cm}cm x {constants.van_max_height_cm}cm
- Best for: Medium to large items, multiple items

Truck Limits:
- Maximum weight: {constants.truck_max_weight_kg}kg
- Best for: Very heavy or bulk orders

Additional Fees:
- Delivery helper/assembly assistance: UGX {constants.helper_fee_ugx}
- Extra care for fragile/valuable items: UGX {constants.extra_care_fee_ugx}

Use these limits to determine the most appropriate delivery method for customer orders.
"""
            doc = Document(
                text=content,
                doc_id="shipping_constants",
                metadata={
                    "type": "shipping_config",
                    "boda_max_weight": float(constants.boda_max_weight_kg),
                    "van_max_weight": float(constants.van_max_weight_kg),
                    "helper_fee": float(constants.helper_fee_ugx),
                    "extra_care_fee": float(constants.extra_care_fee_ugx)
                }
            )
            documents.append(doc)
        except Exception as e:
            print(f"Warning: Could not load shipping constants: {e}")

        # Load shipping zones with rates
        zones = ShippingZone.objects.prefetch_related('areas', 'rates').all()
        for zone in zones:
            # Build area list
            areas = zone.areas.all()
            area_names = [area.area_name for area in areas]
            landmarks = [area.area_name for area in areas if area.is_landmark]

            # Build rates information
            rates_info = []
            for rate in zone.rates.filter(is_active=True):
                delivery_time = f"{rate.min_delivery_hours}-{rate.max_delivery_hours} hours" if rate.min_delivery_hours else "Standard timing"
                rates_info.append(
                    f"  - {rate.get_delivery_method_display()} ({rate.get_service_level_display()}): "
                    f"UGX {rate.base_price_ugx} base + UGX {rate.per_km_price_ugx}/km | {delivery_time}"
                )

            content = f"""
Delivery Zone: {zone.zone_name} ({zone.zone_code})

Coverage:
- Distance from origin: {zone.distance_range_min_km}km to {zone.distance_range_max_km}km
- Estimated delivery: {zone.standard_delivery_days} days (standard), {zone.express_delivery_days} days (express)
- Areas served: {', '.join(area_names)}
- Major landmarks: {', '.join(landmarks) if landmarks else 'None'}

Shipping Rates:
{chr(10).join(rates_info) if rates_info else '  No active rates'}

Description: {zone.description}

When customers mention any of these areas ({', '.join(area_names)}), they are in the {zone.zone_name} zone.
Use this information to calculate shipping costs and delivery times.
"""

            doc = Document(
                text=content,
                doc_id=f"shipping_zone_{zone.id}",
                metadata={
                    "type": "shipping_zone",
                    "zone_id": zone.id,
                    "zone_code": zone.zone_code,
                    "zone_name": zone.zone_name,
                    "areas_list": ', '.join(area_names),  # Store as comma-separated string
                    "distance_min_km": float(zone.distance_range_min_km),
                    "distance_max_km": float(zone.distance_range_max_km)
                }
            )
            documents.append(doc)

        return documents


class KnowledgeDocumentLoader:
    """
    Loads business knowledge and FAQs from AIEmbeddedDocument model.
    This allows admins to teach the AI about business policies, common questions, etc.
    """

    @staticmethod
    def load() -> List[Document]:
        """Load FAQ and business knowledge documents"""
        from apps.ai_assistant.models import AIEmbeddedDocument

        documents = []
        knowledge_docs = AIEmbeddedDocument.objects.filter(
            document_type='faq'
        ).all()

        for doc_model in knowledge_docs:
            doc = Document(
                text=doc_model.content,
                doc_id=f"knowledge_{doc_model.id}",  # Unique ID for updates
                metadata={
                    "type": "faq",
                    "document_id": doc_model.id,
                    **doc_model.metadata
                }
            )
            documents.append(doc)

        return documents


class MasterDocumentLoader:
    """
    Master loader that combines all document loaders.
    This is the main entry point for indexing all knowledge.
    """

    @staticmethod
    def load_all() -> List[Document]:
        """Load all documents from all sources"""
        all_documents = []

        # Load from each loader
        loaders = [
            CategoryDocumentLoader,
            ProductDocumentLoader,
            PartOptionDocumentLoader,
            RulesDocumentLoader,
            ShippingDocumentLoader,
            KnowledgeDocumentLoader
        ]

        for loader_class in loaders:
            try:
                documents = loader_class.load()
                all_documents.extend(documents)
                print(f"✓ Loaded {len(documents)} documents from {loader_class.__name__}")
            except Exception as e:
                print(f"✗ Error loading from {loader_class.__name__}: {str(e)}")

        print(f"\nTotal documents loaded: {len(all_documents)}")
        return all_documents
