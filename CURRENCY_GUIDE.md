# Currency Configuration Guide

## Overview

The Marcus E-commerce platform uses a centralized currency configuration system that makes it easy to deploy in different countries with different currencies. All currency formatting is handled consistently across the application.

## Current Configuration

**Default Currency:** UGX (Ugandan Shilling)
- **Symbol:** UGX
- **Decimal Places:** 0 (no cents)
- **Format:** `UGX 10,000`

## How Currency Works

### Backend Configuration
**File:** `server/apps/products/currency_config.py`

The `CurrencyConfig` class provides:
- Currency symbols and names
- Decimal places per currency
- Thousand/decimal separators
- Display formats
- Conversion rates (for multi-currency support)

### Frontend Integration
**File:** `web/shared/utils/currency.ts`

The frontend:
1. Fetches currency config from `/api/categories/currency-config/`
2. Caches the configuration
3. Uses `formatCurrency()` function throughout the app

## Changing Currency for Different Deployments

### Scenario: Deploy in Kenya

**Step 1: Update Backend Configuration**

Edit `server/apps/products/currency_config.py`:

```python
class CurrencyConfig:
    # Change this line:
    DEFAULT_CURRENCY = "KES"  # Changed from "UGX"
```

**Step 2: That's It!**

The entire application will now use Kenyan Shillings:
- All prices displayed as "KSh 1,000"
- Proper decimal formatting (2 decimal places for KES)
- All calculations in KES

**Step 3: Update Existing Database Prices (Optional)**

If you have existing data in UGX, you can convert it:

```python
# Create a Django management command
# server/apps/products/management/commands/convert_currency.py

from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.products.models import PartOption
from apps.products.currency_config import CurrencyConfig

class Command(BaseCommand):
    help = 'Convert prices from one currency to another'

    def handle(self, *args, **kwargs):
        # Convert all PartOption prices from UGX to KES
        conversion_rate = Decimal("0.041")  # 1 UGX = 0.041 KES (example)

        part_options = PartOption.objects.all()
        for option in part_options:
            old_price = option.default_price
            new_price = (old_price * conversion_rate).quantize(Decimal('0.01'))
            option.default_price = new_price
            option.save()

            self.stdout.write(
                f"Updated {option.name}: UGX {old_price} → KSh {new_price}"
            )
```

Run: `python manage.py convert_currency`

## Supported Currencies

The system comes pre-configured with:

| Currency | Code | Symbol | Decimals | Example |
|----------|------|--------|----------|---------|
| Ugandan Shilling | UGX | UGX | 0 | UGX 10,000 |
| Kenyan Shilling | KES | KSh | 2 | KSh 1,000.00 |
| Tanzanian Shilling | TZS | TSh | 0 | TSh 2,500 |
| Rwandan Franc | RWF | RWF | 0 | RWF 1,300 |
| US Dollar | USD | $ | 2 | $100.00 |
| Euro | EUR | € | 2 | €92.00 |
| British Pound | GBP | £ | 2 | £79.00 |

### Adding a New Currency

Edit `server/apps/products/currency_config.py`:

```python
class CurrencyConfig:
    # Add to CURRENCY_SYMBOLS
    CURRENCY_SYMBOLS = {
        # ... existing ...
        "NGN": "₦",  # Nigerian Naira
    }

    # Add to CURRENCY_NAMES
    CURRENCY_NAMES = {
        # ... existing ...
        "NGN": "Nigerian Naira",
    }

    # Add to DECIMAL_PLACES
    DECIMAL_PLACES = {
        # ... existing ...
        "NGN": 2,
    }

    # Add to DISPLAY_FORMAT
    DISPLAY_FORMAT = {
        # ... existing ...
        "NGN": "₦{amount}",
    }

    # Add to CONVERSION_RATES
    CONVERSION_RATES = {
        # ... existing ...
        "NGN": Decimal("1600.00"),  # 1 USD = 1600 NGN
    }
```

Then set: `DEFAULT_CURRENCY = "NGN"`

## Multi-Currency Support (Future Feature)

The system is designed to support multi-currency in the future:

### Scenario: Allow Customers to Choose Currency

**Step 1: Add Currency Field to Orders**

```python
# server/apps/orders/models.py

class Orders(models.Model):
    # ... existing fields ...
    currency = models.CharField(
        max_length=3,
        default=CurrencyConfig.DEFAULT_CURRENCY,
        choices=[
            ('UGX', 'Ugandan Shilling'),
            ('KES', 'Kenyan Shilling'),
            ('USD', 'US Dollar'),
        ]
    )
```

**Step 2: Store Prices in Base Currency**

Keep all prices in the database in one base currency (e.g., USD), then convert on display:

```python
# When displaying:
from apps.products.currency_config import CurrencyConfig

base_price_usd = Decimal("100.00")
customer_currency = "UGX"

display_price = CurrencyConfig.convert(
    base_price_usd,
    from_currency="USD",
    to_currency=customer_currency
)
# Result: 370,000 UGX
```

**Step 3: Frontend Currency Selector**

```tsx
// web/client/components/currency-selector.tsx

import { useState } from 'react'
import { formatCurrency } from '@shared/utils/currency'

export function CurrencySelector() {
  const [currency, setCurrency] = useState('UGX')

  return (
    <select
      value={currency}
      onChange={(e) => setCurrency(e.target.value)}
    >
      <option value="UGX">UGX - Ugandan Shilling</option>
      <option value="KES">KES - Kenyan Shilling</option>
      <option value="USD">USD - US Dollar</option>
    </select>
  )
}
```

## Frontend Usage

### Basic Formatting

```tsx
import { formatCurrency } from '@shared/utils/currency'

// In your component:
const price = 10000

return (
  <div>
    <p>Price: {formatCurrency(price)}</p>
    {/* Displays: "Price: UGX 10,000" */}

    <p>Amount: {formatCurrency(price, { includeSymbol: false })}</p>
    {/* Displays: "Amount: 10,000" */}
  </div>
)
```

### Using the Hook

```tsx
import { useCurrency } from '@shared/utils/currency'

export function ProductCard({ price }: { price: number }) {
  const { formatCurrency, symbol, code } = useCurrency()

  return (
    <div>
      <p>Price: {formatCurrency(price)}</p>
      <p className="text-xs">All prices in {code}</p>
    </div>
  )
}
```

### Initialize on App Start

```tsx
// web/client/App.tsx or main entry point

import { initializeCurrency } from '@shared/utils/currency'
import { useEffect } from 'react'

export function App() {
  useEffect(() => {
    // Load currency config when app starts
    initializeCurrency()
  }, [])

  return <YourApp />
}
```

## Testing Different Currencies

### Quick Test in Development

1. **Change Currency:**
   ```python
   # server/apps/products/currency_config.py
   DEFAULT_CURRENCY = "KES"  # or "USD", "EUR", etc.
   ```

2. **Restart Backend:**
   ```bash
   docker compose restart web
   ```

3. **Reload Frontend:**
   The frontend will automatically fetch the new currency config

4. **Verify:**
   - All prices now display in the new currency
   - Proper decimal places applied
   - Correct thousand separators used

## Database Considerations

### Current Approach: Single Currency

All prices stored as `DecimalField` without currency designation:
- **Pros:** Simple, no migration needed when changing currency
- **Cons:** Can't store products in multiple currencies simultaneously

### Recommended for Single-Country Deployment

Keep current approach. When deploying to a new country:
1. Set `DEFAULT_CURRENCY` for that deployment
2. Enter prices in that currency
3. All formatting handled automatically

### Recommended for Multi-Country Platform

Add currency field to price-related models:

```python
class PartOption(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='UGX')  # ADD THIS
```

Then convert prices on-the-fly based on customer's location/preference.

## Best Practices

1. **Always use `formatCurrency()`** - Never format currency manually in components
2. **Initialize early** - Call `initializeCurrency()` when app starts
3. **Test edge cases** - Test with 0, negative numbers, very large numbers
4. **Document deployment** - Note which currency each deployment uses
5. **Consider taxes** - Different countries have different tax rules
6. **Update conversion rates** - If using multi-currency, update rates regularly

## FAQ

**Q: Can I show prices in multiple currencies on the same page?**
A: Yes, pass different `config` to `formatCurrency()`:

```tsx
const ugxConfig = await fetchCurrencyConfig() // UGX config
const usdPrice = CurrencyConfig.convert(ugxPrice, 'UGX', 'USD')

// Show both:
<p>UGX: {formatCurrency(ugxPrice)}</p>
<p>USD: {formatCurrency(usdPrice, { config: usdConfig })}</p>
```

**Q: Do I need to update the frontend when changing currency?**
A: No! The frontend fetches currency config from the API automatically.

**Q: What if currency config API fails?**
A: The system falls back to UGX with standard formatting.

**Q: Can I change currency without restarting?**
A: Backend change requires restart. Frontend updates automatically on next config fetch.

## Summary

✅ **For Single-Country Deployment:**
- Set `DEFAULT_CURRENCY` in `currency_config.py`
- Enter prices in that currency
- Done!

✅ **For Multi-Country Platform:**
- Keep prices in base currency (USD)
- Add `currency` field to models
- Convert on display based on customer preference

✅ **The System Handles:**
- Symbol placement
- Decimal places
- Thousand separators
- Number formatting
- Consistent display across all pages

This makes it trivial to deploy your platform in different countries! 🌍
