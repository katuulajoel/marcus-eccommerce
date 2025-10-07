from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from .models import ShippingConstants, ShippingZone, ZoneArea, ShippingRate


def calculate_stackable_volume(length_cm, width_cm, height_cm, quantity):
    """
    Calculate volume for stackable items with efficient stacking.
    Assumes diminishing height growth when stacking.
    """
    if quantity == 1:
        volume_cm3 = length_cm * width_cm * height_cm
    else:
        # Efficient stacking: height grows at 50% rate after first item
        total_height = height_cm + ((quantity - 1) * height_cm * Decimal('0.5'))
        volume_cm3 = length_cm * width_cm * total_height

    # Convert cm³ to m³
    volume_m3 = volume_cm3 / Decimal('1000000')
    return volume_m3


def calculate_shipping_requirements(cart_items):
    """
    Analyzes cart items and determines shipping requirements.

    Args:
        cart_items: List of dicts with 'category' (Category object) and 'quantity' (int)

    Returns:
        dict with shipping requirements including method, weight, volume, and reasons
    """
    constants = ShippingConstants.get_instance()

    total_weight_kg = Decimal('0.00')
    total_volume_m3 = Decimal('0.00')
    force_van = False
    requires_helper = False
    requires_extra_care = False
    reasons = []

    for item in cart_items:
        category = item['category']
        quantity = item['quantity']

        # Calculate item totals
        item_weight = category.unit_weight_kg * quantity

        # Calculate volume based on stackability
        if category.stackable:
            item_volume = calculate_stackable_volume(
                category.unit_length_cm,
                category.unit_width_cm,
                category.unit_height_cm,
                quantity
            )
        else:
            # Non-stackable: volume grows linearly
            volume_cm3 = (category.unit_length_cm * category.unit_width_cm *
                         category.unit_height_cm * quantity)
            item_volume = volume_cm3 / Decimal('1000000')

        total_weight_kg += item_weight
        total_volume_m3 += item_volume

        # Check quantity threshold for boda
        if quantity > category.max_boda_quantity:
            force_van = True
            reasons.append(
                f"{quantity} {category.name}(s) exceeds boda quantity limit of {category.max_boda_quantity}"
            )

        # Check individual item dimensions against boda limits
        if (category.unit_length_cm > constants.boda_max_length_cm or
            category.unit_width_cm > constants.boda_max_width_cm or
            category.unit_height_cm > constants.boda_max_height_cm):
            force_van = True
            reasons.append(f"{category.name} dimensions too large for boda boda")

        # Check if category never allows boda
        if category.max_boda_quantity == 0:
            force_van = True
            if f"{category.name} dimensions too large for boda boda" not in reasons:
                reasons.append(f"{category.name} requires van/pickup delivery")

        # Check special requirements
        if category.requires_helper:
            requires_helper = True
        if category.requires_extra_care:
            requires_extra_care = True

    # Final weight check
    if total_weight_kg > constants.boda_max_weight_kg and not force_van:
        force_van = True
        reasons.append(
            f"Total weight ({total_weight_kg}kg) exceeds boda boda limit ({constants.boda_max_weight_kg}kg)"
        )

    # Determine delivery method
    if force_van:
        if total_weight_kg > constants.van_max_weight_kg:
            method = 'truck'
            reasons.append(f"Total weight ({total_weight_kg}kg) requires truck delivery")
        else:
            method = 'van'
    else:
        method = 'boda'

    if not reasons:
        reasons = ['Standard delivery based on order size']

    return {
        'method': method,
        'requires_helper': requires_helper,
        'requires_extra_care': requires_extra_care,
        'total_weight_kg': total_weight_kg,
        'total_volume_m3': total_volume_m3,
        'reasons': reasons
    }


def get_shipping_options(cart_items, zone):
    """
    Get available shipping options with pricing for a given cart and zone.

    Args:
        cart_items: List of dicts with 'category' and 'quantity'
        zone: ShippingZone object

    Returns:
        List of shipping option dicts with method, cost, delivery time, etc.
    """
    # Get shipping requirements
    requirements = calculate_shipping_requirements(cart_items)
    constants = ShippingConstants.get_instance()

    # Get available rates for this zone and method
    rates = ShippingRate.objects.filter(
        zone=zone,
        delivery_method=requirements['method'],
        is_active=True
    ).order_by('service_level')

    shipping_options = []

    for rate in rates:
        # Calculate base shipping cost
        base_cost = rate.base_price_ugx

        # For van/truck, add per-km charges based on zone's average distance
        if requirements['method'] in ['van', 'truck']:
            avg_distance = (zone.distance_range_min_km + zone.distance_range_max_km) / 2
            # Only charge for distance beyond first 5km
            extra_distance = max(Decimal('0.00'), avg_distance - Decimal('5.00'))
            base_cost += (extra_distance * rate.per_km_price_ugx)

        # Add helper fee if required
        helper_fee = constants.helper_fee_ugx if requirements['requires_helper'] else Decimal('0.00')

        # Add extra care fee if required
        extra_care_fee = constants.extra_care_fee_ugx if requirements['requires_extra_care'] else Decimal('0.00')

        # Calculate total cost
        total_cost = base_cost + helper_fee + extra_care_fee

        # Calculate estimated delivery date
        if rate.service_level == 'standard':
            delivery_days = zone.standard_delivery_days
        else:  # express
            delivery_days = zone.express_delivery_days

        estimated_delivery_date = timezone.now().date() + timedelta(days=delivery_days)

        # Build delivery time description
        if rate.min_delivery_hours and rate.max_delivery_hours:
            if rate.max_delivery_hours < 24:
                delivery_time = f"{rate.min_delivery_hours}-{rate.max_delivery_hours} hours"
            else:
                delivery_time = f"{delivery_days} day{'s' if delivery_days > 1 else ''}"
        else:
            delivery_time = f"{delivery_days} day{'s' if delivery_days > 1 else ''}"

        shipping_option = {
            'rate_id': rate.id,
            'delivery_method': requirements['method'],
            'delivery_method_display': rate.get_delivery_method_display(),
            'service_level': rate.service_level,
            'service_level_display': rate.get_service_level_display(),
            'base_cost_ugx': float(base_cost),
            'helper_fee_ugx': float(helper_fee),
            'extra_care_fee_ugx': float(extra_care_fee),
            'total_cost_ugx': float(total_cost),
            'delivery_time': delivery_time,
            'estimated_delivery_date': estimated_delivery_date.isoformat(),
            'total_weight_kg': float(requirements['total_weight_kg']),
            'total_volume_m3': float(requirements['total_volume_m3']),
            'requires_helper': requirements['requires_helper'],
            'requires_extra_care': requirements['requires_extra_care'],
            'reasons': requirements['reasons'],
        }

        shipping_options.append(shipping_option)

    return shipping_options


def match_address_to_zone(address_string, city=None):
    """
    Match an address string to a shipping zone.

    Args:
        address_string: Full address or area name
        city: City name (optional, for better matching)

    Returns:
        ShippingZone object or None if no match found
    """
    address_lower = address_string.lower()

    # Try exact match first (landmarks and areas)
    zone_areas = ZoneArea.objects.select_related('zone').filter(
        zone__is_active=True
    ).order_by('-is_landmark', 'area_name')

    # Priority 1: Check landmarks
    for area in zone_areas.filter(is_landmark=True):
        if area.area_name.lower() in address_lower:
            return area.zone
        # Check keywords
        for keyword in area.keywords:
            if keyword.lower() in address_lower:
                return area.zone

    # Priority 2: Check regular areas
    for area in zone_areas.filter(is_landmark=False):
        if area.area_name.lower() in address_lower:
            return area.zone
        # Check keywords
        for keyword in area.keywords:
            if keyword.lower() in address_lower:
                return area.zone

    # No match found
    return None


def get_zone_suggestions(partial_name):
    """
    Get zone area suggestions for autocomplete.

    Args:
        partial_name: Partial area name to search

    Returns:
        List of dicts with area_name and zone info
    """
    areas = ZoneArea.objects.select_related('zone').filter(
        area_name__icontains=partial_name,
        zone__is_active=True
    ).order_by('-is_landmark', 'area_name')[:10]

    suggestions = []
    for area in areas:
        suggestions.append({
            'area_name': area.area_name,
            'zone_id': area.zone.id,
            'zone_code': area.zone.zone_code,
            'zone_name': area.zone.zone_name,
            'is_landmark': area.is_landmark
        })

    return suggestions
