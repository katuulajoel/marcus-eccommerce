# Marcus Custom Bikes - Setup Guide

This guide covers setup for the authentication, payments, and order management features.

## Backend Setup

### 1. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 2. Run Database Migrations

```bash
# Make migrations for the new models
docker compose exec web python manage.py makemigrations authentication
docker compose exec web python manage.py makemigrations payments

# Apply all migrations
docker compose exec web python manage.py migrate
```

### 3. Start Services with Docker Compose

The new `docker-compose.yml` includes MailHog for email testing:

```bash
cd server
docker compose up --build -d
```

Services:
- **Django API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **MailHog Web UI**: http://localhost:8025 (view emails)
- **MailHog SMTP**: localhost:1025 (email server)

### 4. Configure Payment Gateways

You need to add payment gateway configurations via Django admin or API.

#### Option A: Via Django Admin

1. Go to http://localhost:8000/admin/
2. Navigate to Payment Gateway Configs
3. Add configurations for each gateway:

**Stripe Configuration:**
```
Gateway Name: stripe
API Key: pk_test_YOUR_PUBLISHABLE_KEY
API Secret: sk_test_YOUR_SECRET_KEY
Environment: sandbox
Webhook Secret: whsec_YOUR_WEBHOOK_SECRET
Is Active: ✓
```

**MTN MoMo Configuration:**
```
Gateway Name: mtn_momo
API Key: YOUR_SUBSCRIPTION_KEY
Additional Config:
{
  "api_user": "YOUR_API_USER_ID",
  "callback_url": "http://your-domain.com/api/payments/webhooks/mtn-momo/"
}
API Secret: YOUR_API_KEY
Environment: sandbox
Is Active: ✓
```

**Airtel Money Configuration:**
```
Gateway Name: airtel_money
API Key: YOUR_CLIENT_ID
API Secret: YOUR_CLIENT_SECRET
Environment: sandbox
Additional Config:
{
  "country": "UG",
  "callback_url": "http://your-domain.com/api/payments/webhooks/airtel/"
}
Is Active: ✓
```

#### Option B: Via Python Shell

```python
docker compose exec web python manage.py shell

from apps.payments.models import PaymentGatewayConfig

# Stripe
PaymentGatewayConfig.objects.create(
    gateway_name='stripe',
    api_key='pk_test_YOUR_PUBLISHABLE_KEY',
    api_secret='sk_test_YOUR_SECRET_KEY',
    environment='sandbox',
    webhook_secret='whsec_YOUR_WEBHOOK_SECRET',
    is_active=True
)

# MTN MoMo
PaymentGatewayConfig.objects.create(
    gateway_name='mtn_momo',
    api_key='YOUR_SUBSCRIPTION_KEY',
    api_secret='YOUR_API_KEY',
    environment='sandbox',
    is_active=True,
    additional_config={
        'api_user': 'YOUR_API_USER_ID',
        'callback_url': 'http://your-domain.com/api/payments/webhooks/mtn-momo/'
    }
)

# Airtel Money
PaymentGatewayConfig.objects.create(
    gateway_name='airtel_money',
    api_key='YOUR_CLIENT_ID',
    api_secret='YOUR_CLIENT_SECRET',
    environment='sandbox',
    is_active=True,
    additional_config={
        'country': 'UG',
        'callback_url': 'http://your-domain.com/api/payments/webhooks/airtel/'
    }
)
```

### 5. Environment Variables

Create or update `server/.env`:

```env
# Database
DATABASE_URL=postgresql://ecommerce_user:ecommerce_password@db:5432/ecommerce_db

# Email (MailHog for development)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mailhog
EMAIL_PORT=1025

# Frontend URL
FRONTEND_URL=http://localhost:3000

# For production, use real SMTP:
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd web
npm install
```

### 2. Environment Configuration

Create `web/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
# From web directory
npm run dev:client
```

The client will be available at http://localhost:3000

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (returns JWT tokens)
- `POST /api/auth/logout/` - Logout (blacklist token)
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/verify-email/<token>/` - Verify email
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password with token
- `GET /api/auth/me/` - Get current user info

### Payments

- `GET /api/payments/gateways/` - List available payment gateways
- `POST /api/payments/initiate/` - Initiate payment
- `POST /api/payments/verify/` - Verify payment status
- `GET /api/payments/transactions/` - List user's transactions
- `POST /api/payments/webhooks/stripe/` - Stripe webhook
- `POST /api/payments/webhooks/mtn-momo/` - MTN MoMo webhook
- `POST /api/payments/webhooks/airtel/` - Airtel Money webhook

### Orders

- `GET /api/orders/` - List user's orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/:id/` - Get order details
- `POST /api/orders/:id/record_payment/` - Record payment for order

## Testing Payment Gateways

### Stripe

Use test cards from: https://stripe.com/docs/testing

- Success: `4242 4242 4242 4242`
- Declined: `4000 0000 0000 0002`
- Use any future expiry date and any 3-digit CVC

### MTN MoMo Sandbox

1. Register at https://momodeveloper.mtn.com/
2. Get sandbox credentials
3. Use test phone numbers from MTN documentation

### Airtel Money Sandbox

1. Register at https://developers.airtel.africa/
2. Get sandbox credentials
3. Use test phone numbers from Airtel documentation

## Testing Email Functionality

1. Trigger an email (register user, reset password)
2. Open MailHog UI at http://localhost:8025
3. View the sent email

## User Flow

### Registration & Login

1. User registers at `/register`
2. Verification email sent (check MailHog)
3. User can login immediately at `/login`
4. JWT tokens stored in localStorage

### Checkout & Payment

1. User adds items to cart (localStorage)
2. User proceeds to checkout (requires login)
3. User enters shipping address
4. User selects payment method
5. Order created in database
6. Payment initiated with selected gateway
7. For mobile money: User approves on phone
8. Payment verified via polling/webhook
9. Order status updated

### Order Management

1. User views orders at `/orders`
2. User clicks order to see details at `/orders/:id`
3. If balance due, user can make additional payment
4. User can track fulfillment status

## Production Considerations

1. **Email**: Switch from MailHog to real SMTP (Gmail, SendGrid, etc.)
2. **Payment Gateways**: Use production API keys and set `environment='production'`
3. **Webhooks**: Configure public webhook URLs in gateway dashboards
4. **CORS**: Update CORS settings to only allow your frontend domain
5. **JWT Secret**: Use strong secret key (change `SECRET_KEY` in settings)
6. **HTTPS**: Use HTTPS for all production endpoints
7. **Stripe Integration**: Implement proper Stripe Elements for PCI compliance

## Common Issues

### Emails not sending
- Check MailHog is running: `docker compose ps`
- Verify EMAIL_HOST setting points to 'mailhog'

### Payment initialization fails
- Check payment gateway configuration exists and is active
- Verify API credentials are correct
- Check Django logs: `docker compose logs web`

### Token expired errors
- Token lifetime is 60 minutes by default
- Frontend should refresh token automatically
- Clear localStorage and login again if issues persist

### Migration errors
- Ensure database is running: `docker compose ps db`
- Drop and recreate database if needed (development only)

## Architecture Overview

### Payment Gateway Pattern

The payment system uses the **Factory Pattern** with a base `AbstractPaymentGateway` class. Each gateway (Stripe, MTN MoMo, Airtel) extends this base class.

To add a new payment gateway:

1. Create new gateway class in `apps/payments/gateways/`
2. Extend `AbstractPaymentGateway`
3. Implement required methods
4. Register in `PaymentService.GATEWAYS`
5. Add gateway choice to models

### Authentication Flow

1. User registers → Customer profile created → Verification email sent
2. User logs in → JWT tokens issued
3. Frontend stores tokens in localStorage
4. Axios interceptor adds token to requests
5. Token refresh handled automatically on 401 errors

## Support

For issues or questions, please check:
- Django logs: `docker compose logs web -f`
- PostgreSQL logs: `docker compose logs db -f`
- Browser console for frontend errors
- Network tab for API call details
