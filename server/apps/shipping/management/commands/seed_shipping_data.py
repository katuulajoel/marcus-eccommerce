from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.shipping.models import ShippingConstants, ShippingZone, ZoneArea, ShippingRate


class Command(BaseCommand):
    help = 'Seed shipping zones, areas, rates, and constants for Uganda'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting shipping data seeding...'))

        # 1. Create/Update Shipping Constants
        self.stdout.write('Creating shipping constants...')
        constants, created = ShippingConstants.objects.get_or_create(pk=1)
        constants.boda_max_weight_kg = Decimal('15.00')
        constants.boda_max_length_cm = Decimal('60.00')
        constants.boda_max_width_cm = Decimal('40.00')
        constants.boda_max_height_cm = Decimal('40.00')
        constants.van_max_weight_kg = Decimal('500.00')
        constants.helper_fee_ugx = Decimal('15000.00')
        constants.extra_care_fee_ugx = Decimal('5000.00')
        constants.save()
        self.stdout.write(self.style.SUCCESS(f'✓ Shipping constants {"created" if created else "updated"}'))

        # 2. Create Shipping Zones
        self.stdout.write('\nCreating shipping zones...')
        zones_data = [
            {
                'zone_code': 'KLA-1',
                'zone_name': 'Kampala Central',
                'distance_range_min_km': Decimal('0.00'),
                'distance_range_max_km': Decimal('5.00'),
                'standard_delivery_days': 1,
                'express_delivery_days': 0,
                'description': 'Central Kampala areas within 5km radius',
            },
            {
                'zone_code': 'KLA-2',
                'zone_name': 'Inner Kampala',
                'distance_range_min_km': Decimal('5.00'),
                'distance_range_max_km': Decimal('12.00'),
                'standard_delivery_days': 2,
                'express_delivery_days': 0,
                'description': 'Inner Kampala suburbs 5-12km from center',
            },
            {
                'zone_code': 'KLA-3',
                'zone_name': 'Outer Kampala',
                'distance_range_min_km': Decimal('12.00'),
                'distance_range_max_km': Decimal('25.00'),
                'standard_delivery_days': 3,
                'express_delivery_days': 1,
                'description': 'Outer Kampala and Greater Kampala 12-25km',
            },
            {
                'zone_code': 'KLA-4',
                'zone_name': 'Extended Kampala',
                'distance_range_min_km': Decimal('25.00'),
                'distance_range_max_km': Decimal('40.00'),
                'standard_delivery_days': 4,
                'express_delivery_days': 2,
                'description': 'Extended Kampala region including Entebbe, Mukono',
            },
        ]

        zones = {}
        for zone_data in zones_data:
            zone, created = ShippingZone.objects.update_or_create(
                zone_code=zone_data['zone_code'],
                defaults=zone_data
            )
            zones[zone.zone_code] = zone
            self.stdout.write(self.style.SUCCESS(f'  ✓ {zone.zone_name} ({zone.zone_code})'))

        # 3. Create Zone Areas
        self.stdout.write('\nCreating zone areas...')
        areas_data = {
            'KLA-1': [
                ('Nakasero', True, ['nakasero hill']),
                ('Kololo', False, ['kololo hill']),
                ('Naguru', False, []),
                ('City Center', True, ['kampala city', 'downtown']),
                ('Industrial Area', False, ['industrial']),
                ('Bugolobi', False, []),
                ('Garden City', True, ['garden city mall']),
            ],
            'KLA-2': [
                ('Ntinda', False, ['ntinda complex']),
                ('Bukoto', False, []),
                ('Naalya', False, []),
                ('Muyenga', False, []),
                ('Wandegeya', False, []),
                ('Makerere', False, ['makerere university']),
                ('Kawempe', False, []),
                ('Rubaga', False, []),
                ('Mulago', False, ['mulago hospital']),
                ('Kabalagala', False, []),
                ('Acacia Mall', True, ['acacia']),
            ],
            'KLA-3': [
                ('Kira', False, ['kira town']),
                ('Nanganda', False, []),
                ('Namugongo', False, []),
                ('Kyanja', False, []),
                ('Lubowa', False, []),
                ('Kajjansi', False, []),
                ('Nsambya', False, []),
                ('Bweyogerere', False, []),
            ],
            'KLA-4': [
                ('Entebbe', False, ['entebbe airport']),
                ('Mukono', False, ['mukono town']),
                ('Wakiso', False, ['wakiso town']),
                ('Mpigi', False, []),
            ],
        }

        for zone_code, areas_list in areas_data.items():
            zone = zones[zone_code]
            for area_name, is_landmark, keywords in areas_list:
                area, created = ZoneArea.objects.update_or_create(
                    zone=zone,
                    area_name=area_name,
                    defaults={
                        'is_landmark': is_landmark,
                        'keywords': keywords
                    }
                )
                symbol = '📍' if is_landmark else '  '
                self.stdout.write(f'  {symbol} {area_name} → {zone_code}')

        # 4. Create Shipping Rates
        self.stdout.write('\nCreating shipping rates...')
        rates_data = [
            # Zone 1 - Kampala Central
            {
                'zone_code': 'KLA-1',
                'delivery_method': 'boda',
                'service_level': 'standard',
                'base_price_ugx': Decimal('5000.00'),
                'per_km_price_ugx': Decimal('0.00'),
                'min_delivery_hours': 4,
                'max_delivery_hours': 24,
            },
            {
                'zone_code': 'KLA-1',
                'delivery_method': 'boda',
                'service_level': 'express',
                'base_price_ugx': Decimal('10000.00'),
                'per_km_price_ugx': Decimal('0.00'),
                'min_delivery_hours': 2,
                'max_delivery_hours': 4,
            },
            {
                'zone_code': 'KLA-1',
                'delivery_method': 'van',
                'service_level': 'standard',
                'base_price_ugx': Decimal('30000.00'),
                'per_km_price_ugx': Decimal('2500.00'),
                'min_delivery_hours': 4,
                'max_delivery_hours': 24,
            },
            {
                'zone_code': 'KLA-1',
                'delivery_method': 'van',
                'service_level': 'express',
                'base_price_ugx': Decimal('45000.00'),
                'per_km_price_ugx': Decimal('3000.00'),
                'min_delivery_hours': 2,
                'max_delivery_hours': 6,
            },

            # Zone 2 - Inner Kampala
            {
                'zone_code': 'KLA-2',
                'delivery_method': 'boda',
                'service_level': 'standard',
                'base_price_ugx': Decimal('8000.00'),
                'per_km_price_ugx': Decimal('0.00'),
                'min_delivery_hours': 6,
                'max_delivery_hours': 48,
            },
            {
                'zone_code': 'KLA-2',
                'delivery_method': 'boda',
                'service_level': 'express',
                'base_price_ugx': Decimal('15000.00'),
                'per_km_price_ugx': Decimal('0.00'),
                'min_delivery_hours': 4,
                'max_delivery_hours': 6,
            },
            {
                'zone_code': 'KLA-2',
                'delivery_method': 'van',
                'service_level': 'standard',
                'base_price_ugx': Decimal('35000.00'),
                'per_km_price_ugx': Decimal('2500.00'),
                'min_delivery_hours': 6,
                'max_delivery_hours': 48,
            },
            {
                'zone_code': 'KLA-2',
                'delivery_method': 'van',
                'service_level': 'express',
                'base_price_ugx': Decimal('50000.00'),
                'per_km_price_ugx': Decimal('3000.00'),
                'min_delivery_hours': 4,
                'max_delivery_hours': 8,
            },

            # Zone 3 - Outer Kampala
            {
                'zone_code': 'KLA-3',
                'delivery_method': 'boda',
                'service_level': 'standard',
                'base_price_ugx': Decimal('12000.00'),
                'per_km_price_ugx': Decimal('0.00'),
                'min_delivery_hours': 24,
                'max_delivery_hours': 72,
            },
            {
                'zone_code': 'KLA-3',
                'delivery_method': 'boda',
                'service_level': 'express',
                'base_price_ugx': Decimal('20000.00'),
                'per_km_price_ugx': Decimal('0.00'),
                'min_delivery_hours': 6,
                'max_delivery_hours': 24,
            },
            {
                'zone_code': 'KLA-3',
                'delivery_method': 'van',
                'service_level': 'standard',
                'base_price_ugx': Decimal('40000.00'),
                'per_km_price_ugx': Decimal('2500.00'),
                'min_delivery_hours': 24,
                'max_delivery_hours': 72,
            },
            {
                'zone_code': 'KLA-3',
                'delivery_method': 'van',
                'service_level': 'express',
                'base_price_ugx': Decimal('60000.00'),
                'per_km_price_ugx': Decimal('3000.00'),
                'min_delivery_hours': 6,
                'max_delivery_hours': 24,
            },

            # Zone 4 - Extended Kampala
            {
                'zone_code': 'KLA-4',
                'delivery_method': 'boda',
                'service_level': 'standard',
                'base_price_ugx': Decimal('18000.00'),
                'per_km_price_ugx': Decimal('0.00'),
                'min_delivery_hours': 48,
                'max_delivery_hours': 96,
            },
            {
                'zone_code': 'KLA-4',
                'delivery_method': 'boda',
                'service_level': 'express',
                'base_price_ugx': Decimal('30000.00'),
                'per_km_price_ugx': Decimal('0.00'),
                'min_delivery_hours': 24,
                'max_delivery_hours': 48,
            },
            {
                'zone_code': 'KLA-4',
                'delivery_method': 'van',
                'service_level': 'standard',
                'base_price_ugx': Decimal('50000.00'),
                'per_km_price_ugx': Decimal('2500.00'),
                'min_delivery_hours': 48,
                'max_delivery_hours': 96,
            },
            {
                'zone_code': 'KLA-4',
                'delivery_method': 'van',
                'service_level': 'express',
                'base_price_ugx': Decimal('75000.00'),
                'per_km_price_ugx': Decimal('3000.00'),
                'min_delivery_hours': 24,
                'max_delivery_hours': 48,
            },
        ]

        for rate_data in rates_data:
            zone_code = rate_data.pop('zone_code')
            zone = zones[zone_code]

            rate, created = ShippingRate.objects.update_or_create(
                zone=zone,
                delivery_method=rate_data['delivery_method'],
                service_level=rate_data['service_level'],
                defaults=rate_data
            )

            method_icon = '🏍️' if rate.delivery_method == 'boda' else '🚐'
            level_icon = '⚡' if rate.service_level == 'express' else '📦'

            self.stdout.write(
                f'  {method_icon} {level_icon} {zone_code} - '
                f'{rate.get_delivery_method_display()} ({rate.get_service_level_display()}) - '
                f'UGX {rate.base_price_ugx:,.0f}'
            )

        self.stdout.write(self.style.SUCCESS('\n✅ Shipping data seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS(f'   - {ShippingZone.objects.count()} zones created'))
        self.stdout.write(self.style.SUCCESS(f'   - {ZoneArea.objects.count()} areas created'))
        self.stdout.write(self.style.SUCCESS(f'   - {ShippingRate.objects.count()} rates created'))
