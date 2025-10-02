"""
Signal handlers for automatic image cleanup in preconfigured_products app.
"""
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import PreConfiguredProduct
from utils.image_cleanup import delete_image_file, get_old_image


@receiver(pre_save, sender=PreConfiguredProduct)
def preconfigured_product_pre_save(sender, instance, **kwargs):
    """
    Delete old image when preconfigured product image is updated.
    """
    if instance.pk:
        old_image = get_old_image(instance, 'image')
        new_image = instance.image

        # If image changed, delete the old one
        if old_image and old_image != new_image:
            delete_image_file(old_image)


@receiver(post_delete, sender=PreConfiguredProduct)
def preconfigured_product_post_delete(sender, instance, **kwargs):
    """
    Delete image file when preconfigured product is deleted.
    """
    if instance.image:
        delete_image_file(instance.image)
