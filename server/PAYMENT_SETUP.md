# Payment Gateway Configuration

This guide explains how to configure payment gateways for the Marcus E-commerce platform.

## Overview

The system supports three payment gateways:
- **Stripe**: For credit/debit card payments
- **MTN Mobile Money**: For MTN mobile money payments in Uganda
- **Airtel Money**: For Airtel mobile money payments in Uganda

## Configuration

### 1. Environment Variables

Payment gateway credentials are stored in the `.env` file and automatically seeded into the database when the Docker container starts.

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cd server
cp .env.example .env
```

### 2. Add Your API Keys

Edit the `.env` file and add your payment gateway credentials:

```env
# Payment Gateway Configuration
PAYMENT_ENVIRONMENT=sandbox  # or 'production'

# Stripe
STRIPE_API_KEY=sk_test_your_stripe_api_key
STRIPE_API_SECRET=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# MTN Mobile Money
MTN_API_KEY=your_mtn_api_key
MTN_API_SECRET=your_mtn_api_secret
MTN_WEBHOOK_SECRET=your_mtn_webhook_secret
MTN_CALLBACK_URL=http://localhost:8000/api/payments/mtn/callback
MTN_SUBSCRIPTION_KEY=your_mtn_subscription_key

# Airtel Money
AIRTEL_API_KEY=your_airtel_api_key
AIRTEL_API_SECRET=your_airtel_api_secret
AIRTEL_WEBHOOK_SECRET=your_airtel_webhook_secret
AIRTEL_CALLBACK_URL=http://localhost:8000/api/payments/airtel/callback
```

### 3. Automatic Seeding

When you start the Docker containers, the payment gateway configurations are automatically seeded into the database:

```bash
docker compose up --build
```

The seeding process:
1. Reads credentials from environment variables
2. Creates or updates `PaymentGatewayConfig` entries in the database
3. Sets gateways as active only if API keys are provided
4. Configures gateway-specific settings (currency, callback URLs, etc.)

### 4. Manual Seeding

You can also manually seed payment configurations anytime:

```bash
# Using Docker
docker compose exec web python manage.py seed_payment_configs

# Or using the standalone script
docker compose exec web python manage.py shell < scripts/seed_payment_configs.py
```

## Payment Gateway Activation

Gateways are automatically activated based on whether API keys are provided:
- ✅ **Active**: Gateway has valid API key in environment variables
- ❌ **Inactive**: Gateway has no API key configured

You can also manually toggle gateway activation in the Django admin panel at:
`http://localhost:8000/admin/payments/paymentgatewayconfig/`

## Database Model

Payment configurations are stored in the `PaymentGatewayConfig` model:

```python
class PaymentGatewayConfig(models.Model):
    gateway_name = CharField  # 'stripe', 'mtn_momo', 'airtel_money'
    is_active = BooleanField
    api_key = CharField
    api_secret = CharField
    environment = CharField  # 'sandbox' or 'production'
    webhook_secret = CharField
    additional_config = JSONField  # Gateway-specific configs
```

## Testing in Development

For development testing without real payment gateways:

1. Leave payment environment variables empty in `.env`
2. Gateways will be seeded but marked as inactive
3. You can mock payment transactions for testing

## Production Deployment

For production:

1. Set `PAYMENT_ENVIRONMENT=production`
2. Use production API keys for all gateways
3. Configure production webhook URLs
4. Ensure webhook endpoints are secured with HTTPS
5. Test each gateway thoroughly before going live

## Obtaining API Keys

### Stripe
1. Sign up at [stripe.com](https://stripe.com)
2. Go to Dashboard → Developers → API Keys
3. Copy your API keys and webhook secret

### MTN Mobile Money
1. Register at [MTN MoMo Developer Portal](https://momodeveloper.mtn.com/)
2. Create an app and get your credentials
3. Configure your callback URL

### Airtel Money
1. Contact Airtel Uganda for API access
2. Complete their onboarding process
3. Obtain API credentials and configure webhooks

## Troubleshooting

### Payment configs not showing up
```bash
# Check if seeding ran successfully
docker compose logs web | grep "payment"

# Manually run seeding
docker compose exec web python manage.py seed_payment_configs
```

### Configs lost after container restart
- Ensure your `.env` file is properly configured
- Check that environment variables are passed to Docker in `compose.yaml`
- Verify the seeding command runs in the Docker startup sequence

### Gateway not activating
- Verify API key is correctly set in `.env` file
- Check for typos in environment variable names
- Run seeding command manually to see error messages

## Architecture

The payment configuration system:
1. **Environment Variables** → Stored in `.env` file
2. **Docker Compose** → Passes env vars to container
3. **Seeding Command** → Reads env vars and creates DB records
4. **PaymentGatewayConfig Model** → Persists configs in PostgreSQL
5. **Payment Services** → Use configs to process transactions

This ensures configs persist across container restarts while keeping secrets secure in environment variables.
