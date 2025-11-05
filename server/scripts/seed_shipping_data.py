"""
Seed shipping zones, areas, and rates for Marcus Custom Bikes
Run with: python manage.py shell < scripts/seed_shipping_data.py
"""
from decimal import Decimal
from apps.shipping.models import ShippingConstants, ShippingZone, ZoneArea, ShippingRate

def seed_shipping_data():
    print("🚀 Starting shipping data seeding...")

    # 1. Create/Update Shipping Constants
    print("\n📋 Setting up shipping constants...")
    constants = ShippingConstants.get_instance()
    print(f"✅ Shipping constants configured")

    # 2. Create Shipping Zones
    print("\n🌍 Creating shipping zones...")

    zones_data = [
        {
            'zone_code': 'KLA-1',
            'zone_name': 'Kampala Central',
            'distance_range_min_km': Decimal('0.00'),
            'distance_range_max_km': Decimal('5.00'),
            'standard_delivery_days': 1,
            'express_delivery_days': 0,
            'description': 'Central business district and immediate surroundings',
        },
        {
            'zone_code': 'KLA-2',
            'zone_name': 'Inner Kampala',
            'distance_range_min_km': Decimal('5.00'),
            'distance_range_max_km': Decimal('10.00'),
            'standard_delivery_days': 1,
            'express_delivery_days': 0,
            'description': 'Inner Kampala suburbs',
        },
        {
            'zone_code': 'KLA-3',
            'zone_name': 'Greater Kampala',
            'distance_range_min_km': Decimal('10.00'),
            'distance_range_max_km': Decimal('20.00'),
            'standard_delivery_days': 2,
            'express_delivery_days': 1,
            'description': 'Greater Kampala metropolitan area',
        },
        {
            'zone_code': 'KLA-4',
            'zone_name': 'Extended Kampala',
            'distance_range_min_km': Decimal('20.00'),
            'distance_range_max_km': Decimal('40.00'),
            'standard_delivery_days': 3,
            'express_delivery_days': 2,
            'description': 'Outer Kampala and nearby towns',
        },
    ]

    zones = {}
    for zone_data in zones_data:
        zone, created = ShippingZone.objects.get_or_create(
            zone_code=zone_data['zone_code'],
            defaults=zone_data
        )
        zones[zone_data['zone_code']] = zone
        status = "Created" if created else "Updated"
        print(f"  {status}: {zone.zone_name} ({zone.zone_code})")

    # 3. Create Zone Areas (Neighborhoods/Landmarks)
    print("\n📍 Creating zone areas...")

    areas_data = [
        # KLA-1: Kampala Central
        {'zone': 'KLA-1', 'area_name': 'City Centre', 'keywords': ['downtown', 'city'], 'is_landmark': False},
        {'zone': 'KLA-1', 'area_name': 'Kampala Road', 'keywords': ['kampala rd'], 'is_landmark': True},
        {'zone': 'KLA-1', 'area_name': 'Garden City', 'keywords': ['garden city mall'], 'is_landmark': True},
        {'zone': 'KLA-1', 'area_name': 'Nakasero', 'keywords': ['nakasero hill'], 'is_landmark': False},
        {'zone': 'KLA-1', 'area_name': 'Kololo', 'keywords': ['kololo hill'], 'is_landmark': False},
        {'zone': 'KLA-1', 'area_name': 'Makerere', 'keywords': ['mak', 'makerere university'], 'is_landmark': False},

        # KLA-2: Inner Kampala
        {'zone': 'KLA-2', 'area_name': 'Ntinda', 'keywords': ['ntinda complex'], 'is_landmark': False},
        {'zone': 'KLA-2', 'area_name': 'Bukoto', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-2', 'area_name': 'Kamwokya', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-2', 'area_name': 'Kabalagala', 'keywords': ['kabs'], 'is_landmark': False},
        {'zone': 'KLA-2', 'area_name': 'Bugolobi', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-2', 'area_name': 'Naguru', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-2', 'area_name': 'Muyenga', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-2', 'area_name': 'Kisasi', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-2', 'area_name': 'Ntinda Shopping Centre', 'keywords': ['ntinda mall'], 'is_landmark': True},

        # KLA-3: Greater Kampala
        {'zone': 'KLA-3', 'area_name': 'Najera', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-3', 'area_name': 'Kira', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-3', 'area_name': 'Kyanja', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-3', 'area_name': 'Naalya', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-3', 'area_name': 'Lubowa', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-3', 'area_name': 'Munyonyo', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-3', 'area_name': 'Entebbe Road', 'keywords': ['entebbe'], 'is_landmark': False},
        {'zone': 'KLA-3', 'area_name': 'Nsambya', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-3', 'area_name': 'Mengo', 'keywords': [], 'is_landmark': False},

        # KLA-4: Extended Kampala
        {'zone': 'KLA-4', 'area_name': 'Wakiso', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-4', 'area_name': 'Entebbe', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-4', 'area_name': 'Mukono', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-4', 'area_name': 'Seeta', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-4', 'area_name': 'Namugongo', 'keywords': [], 'is_landmark': False},
        {'zone': 'KLA-4', 'area_name': 'Bweyogerere', 'keywords': ['bweyos'], 'is_landmark': False},
    ]

    created_count = 0
    for area_data in areas_data:
        zone_code = area_data.pop('zone')
        zone = zones[zone_code]
        area, created = ZoneArea.objects.get_or_create(
            zone=zone,
            area_name=area_data['area_name'],
            defaults={
                'keywords': area_data['keywords'],
                'is_landmark': area_data['is_landmark']
            }
        )
        if created:
            created_count += 1

    print(f"  ✅ Created {created_count} zone areas")

    # 4. Create Shipping Rates
    print("\n💰 Creating shipping rates...")

    rates_data = [
        # KLA-1: Kampala Central
        {'zone': 'KLA-1', 'delivery_method': 'boda', 'service_level': 'standard', 'base_price_ugx': Decimal('10000'), 'per_km_price_ugx': Decimal('0'), 'min_hours': 2, 'max_hours': 4},
        {'zone': 'KLA-1', 'delivery_method': 'boda', 'service_level': 'express', 'base_price_ugx': Decimal('15000'), 'per_km_price_ugx': Decimal('0'), 'min_hours': 1, 'max_hours': 2},
        {'zone': 'KLA-1', 'delivery_method': 'van', 'service_level': 'standard', 'base_price_ugx': Decimal('40000'), 'per_km_price_ugx': Decimal('1000'), 'min_hours': 2, 'max_hours': 5},
        {'zone': 'KLA-1', 'delivery_method': 'van', 'service_level': 'express', 'base_price_ugx': Decimal('60000'), 'per_km_price_ugx': Decimal('1500'), 'min_hours': 1, 'max_hours': 3},
        {'zone': 'KLA-1', 'delivery_method': 'truck', 'service_level': 'standard', 'base_price_ugx': Decimal('100000'), 'per_km_price_ugx': Decimal('2000'), 'min_hours': 3, 'max_hours': 6},

        # KLA-2: Inner Kampala
        {'zone': 'KLA-2', 'delivery_method': 'boda', 'service_level': 'standard', 'base_price_ugx': Decimal('15000'), 'per_km_price_ugx': Decimal('0'), 'min_hours': 3, 'max_hours': 6},
        {'zone': 'KLA-2', 'delivery_method': 'boda', 'service_level': 'express', 'base_price_ugx': Decimal('20000'), 'per_km_price_ugx': Decimal('0'), 'min_hours': 2, 'max_hours': 4},
        {'zone': 'KLA-2', 'delivery_method': 'van', 'service_level': 'standard', 'base_price_ugx': Decimal('50000'), 'per_km_price_ugx': Decimal('1200'), 'min_hours': 3, 'max_hours': 6},
        {'zone': 'KLA-2', 'delivery_method': 'van', 'service_level': 'express', 'base_price_ugx': Decimal('70000'), 'per_km_price_ugx': Decimal('1800'), 'min_hours': 2, 'max_hours': 4},
        {'zone': 'KLA-2', 'delivery_method': 'truck', 'service_level': 'standard', 'base_price_ugx': Decimal('120000'), 'per_km_price_ugx': Decimal('2500'), 'min_hours': 4, 'max_hours': 8},

        # KLA-3: Greater Kampala
        {'zone': 'KLA-3', 'delivery_method': 'boda', 'service_level': 'standard', 'base_price_ugx': Decimal('20000'), 'per_km_price_ugx': Decimal('0'), 'min_hours': 24, 'max_hours': 48},
        {'zone': 'KLA-3', 'delivery_method': 'boda', 'service_level': 'express', 'base_price_ugx': Decimal('30000'), 'per_km_price_ugx': Decimal('0'), 'min_hours': 4, 'max_hours': 8},
        {'zone': 'KLA-3', 'delivery_method': 'van', 'service_level': 'standard', 'base_price_ugx': Decimal('70000'), 'per_km_price_ugx': Decimal('1500'), 'min_hours': 24, 'max_hours': 48},
        {'zone': 'KLA-3', 'delivery_method': 'van', 'service_level': 'express', 'base_price_ugx': Decimal('100000'), 'per_km_price_ugx': Decimal('2000'), 'min_hours': 6, 'max_hours': 12},
        {'zone': 'KLA-3', 'delivery_method': 'truck', 'service_level': 'standard', 'base_price_ugx': Decimal('150000'), 'per_km_price_ugx': Decimal('3000'), 'min_hours': 24, 'max_hours': 48},

        # KLA-4: Extended Kampala
        {'zone': 'KLA-4', 'delivery_method': 'van', 'service_level': 'standard', 'base_price_ugx': Decimal('100000'), 'per_km_price_ugx': Decimal('2000'), 'min_hours': 48, 'max_hours': 72},
        {'zone': 'KLA-4', 'delivery_method': 'van', 'service_level': 'express', 'base_price_ugx': Decimal('150000'), 'per_km_price_ugx': Decimal('3000'), 'min_hours': 24, 'max_hours': 48},
        {'zone': 'KLA-4', 'delivery_method': 'truck', 'service_level': 'standard', 'base_price_ugx': Decimal('200000'), 'per_km_price_ugx': Decimal('4000'), 'min_hours': 48, 'max_hours': 96},
    ]

    created_count = 0
    for rate_data in rates_data:
        zone_code = rate_data.pop('zone')
        zone = zones[zone_code]
        min_hours = rate_data.pop('min_hours')
        max_hours = rate_data.pop('max_hours')

        rate, created = ShippingRate.objects.get_or_create(
            zone=zone,
            delivery_method=rate_data['delivery_method'],
            service_level=rate_data['service_level'],
            defaults={
                'base_price_ugx': rate_data['base_price_ugx'],
                'per_km_price_ugx': rate_data['per_km_price_ugx'],
                'min_delivery_hours': min_hours,
                'max_delivery_hours': max_hours,
            }
        )
        if created:
            created_count += 1

    print(f"  ✅ Created {created_count} shipping rates")

    # Summary
    print("\n" + "="*60)
    print("✅ Shipping data seeding completed!")
    print("="*60)
    print(f"📊 Summary:")
    print(f"   - Zones: {ShippingZone.objects.count()}")
    print(f"   - Areas: {ZoneArea.objects.count()}")
    print(f"   - Rates: {ShippingRate.objects.count()}")
    print("="*60)

if __name__ == '__main__':
    seed_shipping_data()
