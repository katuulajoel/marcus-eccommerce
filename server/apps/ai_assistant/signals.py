"""
Django signals to auto-trigger index updates when models change.
This ensures the AI always has up-to-date product information!
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.products.models import Category, PartOption
from apps.preconfigured_products.models import PreConfiguredProduct
from apps.configurator.models import IncompatibilityRule, PriceAdjustmentRule


def schedule_index_update():
    """
    Schedule an index update.
    Uses cache to debounce rapid changes (only update once per minute).
    """
    # Check if update is already scheduled
    if cache.get('ai_index_update_scheduled'):
        return

    # Mark as scheduled
    cache.set('ai_index_update_scheduled', True, timeout=60)  # 1 minute debounce

    # Import here to avoid circular import
    from .tasks import update_ai_index

    # Schedule update (delayed by 30 seconds to batch changes)
    update_ai_index.apply_async(countdown=30)


# Product-related signals
@receiver([post_save, post_delete], sender=PreConfiguredProduct)
def handle_product_change(sender, instance, **kwargs):
    """Trigger index update when products change"""
    schedule_index_update()


@receiver([post_save, post_delete], sender=Category)
def handle_category_change(sender, instance, **kwargs):
    """Trigger index update when categories change"""
    schedule_index_update()


@receiver([post_save, post_delete], sender=PartOption)
def handle_part_option_change(sender, instance, **kwargs):
    """Trigger index update when part options change"""
    schedule_index_update()


@receiver([post_save, post_delete], sender=IncompatibilityRule)
def handle_incompatibility_rule_change(sender, instance, **kwargs):
    """Trigger index update when rules change"""
    schedule_index_update()


@receiver([post_save, post_delete], sender=PriceAdjustmentRule)
def handle_price_rule_change(sender, instance, **kwargs):
    """Trigger index update when price rules change"""
    schedule_index_update()
