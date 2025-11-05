# Shipping Data Seeding Guide

## Issue
The checkout page's shipping zone search and dropdown were not working because the database was missing shipping zone data.

## Solution
A seeding script has been created to populate the database with shipping zones, areas, and rates.

## How to Seed Shipping Data

### Quick Command
```bash
docker compose exec web bash -c "python manage.py shell <<EOF
from scripts.seed_shipping_data import seed_shipping_data
seed_shipping_data()
EOF"
```

### What Gets Seeded

1. **Shipping Constants** (singleton)
   - Boda boda limits (weight, dimensions)
   - Van/Pickup limits
   - Truck limits
   - Additional fees (helper, extra care)

2. **Shipping Zones** (4 zones)
   - KLA-1: Kampala Central (0-5km)
   - KLA-2: Inner Kampala (5-10km)
   - KLA-3: Greater Kampala (10-20km)
   - KLA-4: Extended Kampala (20-40km)

3. **Zone Areas** (30 areas/landmarks)
   - Neighborhoods like Ntinda, Kololo, Bukoto, etc.
   - Landmarks like Garden City, Kampala Road, etc.

4. **Shipping Rates** (18 rates)
   - Multiple delivery methods per zone (boda, van, truck)
   - Multiple service levels (standard, express)
   - Dynamic pricing based on zone and method

## Verification

Check if data exists:
```bash
docker compose exec web python manage.py shell -c "
from apps.shipping.models import ShippingZone, ZoneArea, ShippingRate
print(f'Zones: {ShippingZone.objects.count()}')
print(f'Areas: {ZoneArea.objects.count()}')
print(f'Rates: {ShippingRate.objects.count()}')
"
```

Test the API:
```bash
# Get all zones
curl http://localhost:8000/api/shipping/zones/

# Get zone suggestions
curl "http://localhost:8000/api/shipping/zones/suggest/?q=ntinda"

# Calculate shipping
curl -X POST http://localhost:8000/api/shipping/calculator/calculate/ \
  -H "Content-Type: application/json" \
  -d '{"cart_items": [{"category_id": 1, "quantity": 1}], "zone_id": 1}'
```

## Files Created
- `/server/scripts/seed_shipping_data.py` - Main seeding script
- `/server/apps/shipping/management/commands/seed_shipping_data.py` - Django management command (if needed)

## Next Steps
Consider adding this seeding to:
1. The main `fixtures/seed_data.json` file
2. Docker compose initialization scripts
3. CI/CD pipeline for test environments
