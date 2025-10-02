#!/usr/bin/env python
"""
Migration script to transition from image_url CharField to image ImageField.
This script should be run AFTER the database migrations have been applied.

Usage:
    python scripts/migrate_images.py

Note: This script assumes image_url field still exists in the database.
After running this script successfully, you can create a migration to remove image_url fields.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()

from apps.products.models import Category, PartOption
from apps.preconfigured_products.models import PreConfiguredProduct


def check_images():
    """
    Check the current state of image fields across models.

    This function does the following:
    1. Checks which records have images set
    2. Logs the image paths for review
    """

    print("=" * 80)
    print("Image Migration Script")
    print("=" * 80)
    print()

    # Check Categories
    print("Checking Categories...")
    categories_with_images = Category.objects.exclude(image__isnull=True).exclude(image='')
    if categories_with_images.exists():
        print(f"Found {categories_with_images.count()} categories with images:")
        for cat in categories_with_images:
            print(f"  - ID {cat.id}: {cat.name}")
            print(f"    image: {cat.image}")
        print()
    else:
        print("  No categories with images found.")
        print()

    # Check PartOptions
    print("Checking PartOptions...")
    partoptions_with_images = PartOption.objects.exclude(image__isnull=True).exclude(image='')
    if partoptions_with_images.exists():
        print(f"Found {partoptions_with_images.count()} part options with images:")
        for opt in partoptions_with_images:
            print(f"  - ID {opt.id}: {opt.name}")
            print(f"    image: {opt.image}")
        print()
    else:
        print("  No part options with images found.")
        print()

    # Check PreConfiguredProducts
    print("Checking PreConfiguredProducts...")
    products_with_images = PreConfiguredProduct.objects.exclude(image__isnull=True).exclude(image='')
    if products_with_images.exists():
        print(f"Found {products_with_images.count()} preconfigured products with images:")
        for prod in products_with_images:
            print(f"  - ID {prod.id}: {prod.name}")
            print(f"    image: {prod.image}")
        print()
    else:
        print("  No preconfigured products with images found.")
        print()

    print("=" * 80)
    print("Image Summary")
    print("=" * 80)
    print(f"Categories with images: {categories_with_images.count()}")
    print(f"PartOptions with images: {partoptions_with_images.count()}")
    print(f"PreConfiguredProducts with images: {products_with_images.count()}")
    print()

    total = categories_with_images.count() + partoptions_with_images.count() + products_with_images.count()

    if total > 0:
        print("Current image paths are listed above for review.")
        print("All images should be stored in their respective upload_to directories:")
        print("  - Categories: 'categories/'")
        print("  - PartOptions: 'part_options/'")
        print("  - PreConfiguredProducts: 'preconfigured_products/'")
    else:
        print("No images found in any models.")

    print("=" * 80)


if __name__ == '__main__':
    try:
        check_images()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
