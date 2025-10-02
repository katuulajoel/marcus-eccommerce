"""
Utility functions for image file cleanup.
Helps prevent orphaned image files when models are updated or deleted.
"""
import os
from django.conf import settings


def delete_image_file(image_field):
    """
    Delete the physical file associated with an ImageField.

    Args:
        image_field: Django ImageField instance
    """
    if image_field and hasattr(image_field, 'path'):
        try:
            if os.path.isfile(image_field.path):
                os.remove(image_field.path)

                # Try to remove empty parent directories
                try:
                    parent_dir = os.path.dirname(image_field.path)
                    if not os.listdir(parent_dir):
                        os.rmdir(parent_dir)
                except OSError:
                    pass  # Directory not empty or doesn't exist

        except (ValueError, OSError) as e:
            # File doesn't exist or other OS error
            print(f"Error deleting image file: {e}")


def get_old_image(instance, field_name='image'):
    """
    Get the old image from database before save.

    Args:
        instance: Model instance
        field_name: Name of the image field (default: 'image')

    Returns:
        Old image field value or None
    """
    try:
        if instance.pk:
            old_instance = instance.__class__.objects.get(pk=instance.pk)
            return getattr(old_instance, field_name, None)
    except instance.__class__.DoesNotExist:
        pass
    return None
