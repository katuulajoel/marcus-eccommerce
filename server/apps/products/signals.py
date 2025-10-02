"""
Signal handlers for automatic image cleanup in products app.
"""
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Category, PartOption
from utils.image_cleanup import delete_image_file, get_old_image


@receiver(pre_save, sender=Category)
def category_pre_save(sender, instance, **kwargs):
    """
    Delete old image when category image is updated.
    """
    if instance.pk:
        old_image = get_old_image(instance, 'image')
        new_image = instance.image

        # If image changed, delete the old one
        if old_image and old_image != new_image:
            delete_image_file(old_image)


@receiver(post_delete, sender=Category)
def category_post_delete(sender, instance, **kwargs):
    """
    Delete image file when category is deleted.
    """
    if instance.image:
        delete_image_file(instance.image)


@receiver(pre_save, sender=PartOption)
def part_option_pre_save(sender, instance, **kwargs):
    """
    Delete old image when part option image is updated.
    """
    if instance.pk:
        old_image = get_old_image(instance, 'image')
        new_image = instance.image

        # If image changed, delete the old one
        if old_image and old_image != new_image:
            delete_image_file(old_image)


@receiver(post_delete, sender=PartOption)
def part_option_post_delete(sender, instance, **kwargs):
    """
    Delete image file when part option is deleted.
    """
    if instance.image:
        delete_image_file(instance.image)
