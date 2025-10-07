# Shipping Module - Marcus E-Commerce

## Overview

Uganda-focused shipping system with Kampala delivery zones, quantity-aware shipping escalation, and support for category-based shipping profiles. The system intelligently determines delivery method (boda/van/truck) based on product dimensions, weight, quantity, and special handling requirements.

## Features

### ✅ Completed Backend Features

1. **Category-Based Shipping Profiles**
   - Shipping dimensions and weight defined at category level
   - Stackable item support with smart volume calculation
   - Quantity thresholds for boda vs van delivery
   - Helper and extra care requirements per category

2. **Kampala Delivery Zones**
   - 4 zones covering Kampala and surroundings (KLA-1 to KLA-4)
   - Zone-based pricing for boda and van delivery
   - Standard and express service levels
   - Area/landmark mapping for zone detection

3. **Intelligent Shipping Calculation**
   - Automatic delivery method selection based on cart contents
   - Weight and volume validation against vehicle limits
   - Additional fees for helpers and extra care
   - Detailed calculation reasons for transparency

4. **Complete REST API**
   - `/api/shipping/zones/` - List all zones and areas
   - `/api/shipping/zones/match/` - Match address to zone
   - `/api/shipping/zones/suggest/` - Autocomplete suggestions
   - `/api/shipping/calculator/calculate/` - Calculate shipping options
   - `/api/shipping/rates/` - Get shipping rates

## Database Schema

### Models Created

1. **ShippingConstants** - System-wide limits and fees (singleton)
2. **ShippingZone** - Delivery zones (KLA-1, KLA-2, etc.)
3. **ZoneArea** - Areas/landmarks within zones
4. **ShippingRate** - Pricing per zone/method/service level
5. **OrderShippingMethod** - Tracks shipping for each order

### Category Model Extended

Added shipping profile fields:
- `unit_weight_kg`, `unit_length_cm`, `unit_width_cm`, `unit_height_cm`
- `stackable` (boolean)
- `max_boda_quantity` (0 = never use boda)
- `requires_helper`, `requires_extra_care` (boolean)
- `shipping_notes` (text)

### Orders Model Extended

Added fields:
- `subtotal` - Products total before shipping
- `shipping_cost` - Shipping fee in UGX

## Setup Instructions

### 1. Run Migrations

**IMPORTANT: Docker must be running first!**

```bash
cd server
docker compose up -d
docker compose exec web python manage.py makemigrations products
docker compose exec web python manage.py makemigrations orders
docker compose exec web python manage.py makemigrations shipping
docker compose exec web python manage.py migrate
```

### 2. Seed Shipping Data

```bash
# Seed zones, areas, and rates
docker compose exec web python manage.py seed_shipping_data

# Configure category shipping profiles (Bikes, Surfboards, Skis)
docker compose exec web python manage.py configure_category_shipping
```

### 3. Verify in Django Admin

Access [http://localhost:8000/admin/](http://localhost:8000/admin/) and check:
- Shipping Constants
- Shipping Zones (should see 4 zones)
- Zone Areas (should see ~20+ areas)
- Shipping Rates (should see rates for each zone)

## API Usage Examples

### Calculate Shipping

```bash
curl -X POST http://localhost:8000/api/shipping/calculator/calculate/ \
  -H "Content-Type: application/json" \
  -d '{
    "cart_items": [
      {"category_id": 1, "quantity": 2}
    ],
    "zone_id": 1
  }'
```

Response:
```json
{
  "zone": {
    "id": 1,
    "zone_code": "KLA-1",
    "zone_name": "Kampala Central"
  },
  "shipping_options": [
    {
      "rate_id": 1,
      "delivery_method": "van",
      "service_level": "standard",
      "base_cost_ugx": 30000.0,
      "helper_fee_ugx": 15000.0,
      "extra_care_fee_ugx": 5000.0,
      "total_cost_ugx": 50000.0,
      "delivery_time": "1 day",
      "reasons": ["Bikes require van/pickup delivery"]
    }
  ]
}
```

### Match Address to Zone

```bash
curl -X POST http://localhost:8000/api/shipping/zones/match/ \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Ntinda Complex, Kampala",
    "city": "Kampala"
  }'
```

### Get Zone Suggestions (Autocomplete)

```bash
curl http://localhost:8000/api/shipping/zones/suggest/?q=ntin
```

## Shipping Zones Configuration

### Zone 1 - Kampala Central (0-5km)
**Areas:** Nakasero, Kololo, Naguru, City Center, Industrial Area, Bugolobi

**Rates:**
- Boda Standard: UGX 5,000 (4-24 hours)
- Boda Express: UGX 10,000 (2-4 hours)
- Van Standard: UGX 30,000 base + UGX 2,500/km (4-24 hours)
- Van Express: UGX 45,000 base + UGX 3,000/km (2-6 hours)

### Zone 2 - Inner Kampala (5-12km)
**Areas:** Ntinda, Bukoto, Naalya, Muyenga, Wandegeya, Makerere, Kawempe, Rubaga

**Rates:**
- Boda Standard: UGX 8,000 (6-48 hours)
- Boda Express: UGX 15,000 (4-6 hours)
- Van Standard: UGX 35,000 base + UGX 2,500/km (6-48 hours)
- Van Express: UGX 50,000 base + UGX 3,000/km (4-8 hours)

### Zone 3 - Outer Kampala (12-25km)
**Areas:** Kira, Namugongo, Kyanja, Lubowa, Kajjansi, Nsambya, Bweyogerere

**Rates:**
- Boda Standard: UGX 12,000 (24-72 hours)
- Boda Express: UGX 20,000 (6-24 hours)
- Van Standard: UGX 40,000 base + UGX 2,500/km (24-72 hours)
- Van Express: UGX 60,000 base + UGX 3,000/km (6-24 hours)

### Zone 4 - Extended Kampala (25-40km)
**Areas:** Entebbe, Mukono, Wakiso, Mpigi

**Rates:**
- Boda Standard: UGX 18,000 (48-96 hours)
- Boda Express: UGX 30,000 (24-48 hours)
- Van Standard: UGX 50,000 base + UGX 2,500/km (48-96 hours)
- Van Express: UGX 75,000 base + UGX 3,000/km (24-48 hours)

### Additional Fees
- **Helper Fee:** UGX 15,000 (for items requiring assembly/assistance)
- **Extra Care Fee:** UGX 5,000 (for fragile/valuable items)

## Category Shipping Profiles

### Bikes
- Weight: 12.5kg | Dimensions: 180×60×90cm
- Max Boda Qty: 0 (van/pickup only)
- Requires Helper: ✓ | Extra Care: ✓

### Surfboards
- Weight: 8kg | Dimensions: 220×50×10cm
- Max Boda Qty: 0 (too long for boda)
- Requires Helper: ✗ | Extra Care: ✓

### Skis
- Weight: 5kg | Dimensions: 180×20×15cm
- Stackable: ✓ | Max Boda Qty: 2
- Requires Helper: ✗ | Extra Care: ✓

## Next Steps (Pending Implementation)

### Backend
1. ✅ Update order creation API to accept shipping method
2. ✅ Recalculate shipping on backend before order creation
3. ✅ Create OrderShippingMethod when order is created
4. ✅ Update order serializer to include shipping details

### Frontend
1. ⏳ Create shipping calculator React hook (`use-shipping-calculator.ts`)
2. ⏳ Create shipping options component (`shipping-options.tsx`)
3. ⏳ Create zone selector component (`zone-selector.tsx`)
4. ⏳ Add shipping step to checkout flow
5. ⏳ Update cart page with shipping estimator
6. ⏳ Update order summary to show shipping breakdown

### Testing
1. ⏳ Test boda-eligible items (small quantities)
2. ⏳ Test quantity exceeding boda limit
3. ⏳ Test large items requiring van
4. ⏳ Test mixed cart scenarios
5. ⏳ Test helper and extra care fee application
6. ⏳ End-to-end order creation with shipping

## File Structure

```
server/apps/shipping/
├── __init__.py
├── admin.py                    # Django admin configuration
├── apps.py                     # App configuration
├── models.py                   # All shipping models
├── serializers.py              # API serializers
├── services.py                 # Business logic (calculation)
├── views.py                    # API views
├── urls.py                     # URL routing
├── README.md                   # This file
├── management/
│   └── commands/
│       ├── seed_shipping_data.py           # Seed zones/rates
│       └── configure_category_shipping.py  # Configure categories
└── migrations/
    └── (generated migration files)
```

## Troubleshooting

### Docker Issues
If you see "Cannot connect to Docker daemon":
```bash
# Start Docker Desktop first
# Then restart containers
cd server
docker compose down
docker compose up -d
```

### Migration Issues
If migrations fail:
```bash
# Check what migrations exist
docker compose exec web python manage.py showmigrations

# Run migrations one app at a time
docker compose exec web python manage.py migrate products
docker compose exec web python manage.py migrate orders
docker compose exec web python manage.py migrate shipping
```

### Seeding Issues
If categories don't exist yet:
```bash
# Create categories first in Django admin or via API
# Then run category shipping configuration
docker compose exec web python manage.py configure_category_shipping
```

## Future Enhancements

- SafeBoda API integration for real-time quotes
- GPS-based zone detection
- Split shipments (boda + van for mixed carts)
- National expansion (Jinja, Mbale, Mbarara, etc.)
- Delivery scheduling (time slots)
- Tracking integration
