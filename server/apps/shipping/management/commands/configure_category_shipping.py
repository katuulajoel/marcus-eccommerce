from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.products.models import Category


class Command(BaseCommand):
    help = 'Configure shipping profiles for product categories'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Configuring category shipping profiles...'))

        # Define shipping profiles for each category
        shipping_profiles = {
            'Bikes': {
                'unit_weight_kg': Decimal('12.50'),
                'unit_length_cm': Decimal('180.00'),
                'unit_width_cm': Decimal('60.00'),
                'unit_height_cm': Decimal('90.00'),
                'stackable': False,
                'max_boda_quantity': 0,  # Never use boda
                'requires_helper': True,
                'requires_extra_care': True,
                'shipping_notes': 'Large item requiring assembly. Van/pickup delivery only.'
            },
            'Surfboards': {
                'unit_weight_kg': Decimal('8.00'),
                'unit_length_cm': Decimal('220.00'),
                'unit_width_cm': Decimal('50.00'),
                'unit_height_cm': Decimal('10.00'),
                'stackable': False,
                'max_boda_quantity': 0,  # Too long for boda
                'requires_helper': False,
                'requires_extra_care': True,
                'shipping_notes': 'Fragile. Handle with care to avoid damage.'
            },
            'Skis': {
                'unit_weight_kg': Decimal('5.00'),
                'unit_length_cm': Decimal('180.00'),
                'unit_width_cm': Decimal('20.00'),
                'unit_height_cm': Decimal('15.00'),
                'stackable': True,
                'max_boda_quantity': 2,  # Up to 2 pairs on boda
                'requires_helper': False,
                'requires_extra_care': True,
                'shipping_notes': 'Can be stacked. Fragile edges.'
            },
        }

        updated_count = 0
        not_found = []

        for category_name, profile in shipping_profiles.items():
            try:
                category = Category.objects.get(name=category_name)

                # Update category with shipping profile
                for field, value in profile.items():
                    setattr(category, field, value)

                category.save()
                updated_count += 1

                # Display summary
                method_icon = '🏍️' if profile['max_boda_quantity'] > 0 else '🚐'
                helper_icon = '👷' if profile['requires_helper'] else '  '
                care_icon = '⚠️' if profile['requires_extra_care'] else '  '

                self.stdout.write(
                    f'  {method_icon} {helper_icon} {care_icon} {category_name}: '
                    f'{profile["unit_weight_kg"]}kg, '
                    f'{profile["unit_length_cm"]}×{profile["unit_width_cm"]}×{profile["unit_height_cm"]}cm, '
                    f'Max boda qty: {profile["max_boda_quantity"]}'
                )

            except Category.DoesNotExist:
                not_found.append(category_name)
                self.stdout.write(self.style.WARNING(f'  ⚠ Category "{category_name}" not found, skipping...'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ {updated_count} categories configured with shipping profiles'))

        if not_found:
            self.stdout.write(self.style.WARNING(f'   Categories not found: {", ".join(not_found)}'))
            self.stdout.write(self.style.WARNING('   Create these categories first, then run this command again.'))

        # Show legend
        self.stdout.write('\nLegend:')
        self.stdout.write('  🏍️ = Boda eligible    🚐 = Van/pickup only')
        self.stdout.write('  👷 = Requires helper   ⚠️ = Requires extra care')
