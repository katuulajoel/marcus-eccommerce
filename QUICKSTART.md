# Quick Start Guide

## ✅ Setup Complete!

Your authentication, payments, and order management system is now ready!

### What's Been Configured

✅ Database migrations applied
✅ Payment gateways configured (Stripe, MTN MoMo, Airtel Money)
✅ Authentication system ready
✅ Email system configured (MailHog)

### Next Steps

#### 1. Update Payment Gateway Credentials (Important!)

The payment gateways have placeholder API keys. Update them with your real credentials:

**Option A: Django Admin (Recommended)**

```bash
# Create a superuser if you haven't already
docker compose exec web python manage.py createsuperuser

# Then visit:
# http://localhost:8000/admin/payments/paymentgatewayconfig/
```

**Option B: Python Shell**

```bash
docker compose exec web python manage.py shell
```

```python
from apps.payments.models import PaymentGatewayConfig

# Update Stripe
stripe = PaymentGatewayConfig.objects.get(gateway_name='stripe')
stripe.api_key = 'pk_test_YOUR_REAL_KEY'  # Publishable key
stripe.api_secret = 'sk_test_YOUR_REAL_SECRET'  # Secret key
stripe.webhook_secret = 'whsec_YOUR_WEBHOOK_SECRET'
stripe.save()

# Update MTN MoMo
momo = PaymentGatewayConfig.objects.get(gateway_name='mtn_momo')
momo.api_key = 'YOUR_SUBSCRIPTION_KEY'
momo.api_secret = 'YOUR_API_KEY'
momo.additional_config['api_user'] = 'YOUR_API_USER_ID'
momo.save()

# Update Airtel Money
airtel = PaymentGatewayConfig.objects.get(gateway_name='airtel_money')
airtel.api_key = 'YOUR_CLIENT_ID'
airtel.api_secret = 'YOUR_CLIENT_SECRET'
airtel.save()
```

#### 2. Get Test Credentials

**Stripe**
- Sign up at https://dashboard.stripe.com/register
- Get test keys from https://dashboard.stripe.com/test/apikeys

**MTN MoMo**
- Sign up at https://momodeveloper.mtn.com/
- Subscribe to Collections product
- Get sandbox credentials

**Airtel Money**
- Sign up at https://developers.airtel.africa/
- Get sandbox credentials

#### 3. Test the System

**Test Email (MailHog)**
1. Register a new user at http://localhost:3000/register
2. View the verification email at http://localhost:8025

**Test Authentication**
1. Visit http://localhost:3000/register
2. Create an account
3. Login at http://localhost:3000/login
4. You should see your user menu in the header

**Test Checkout Flow**
1. Add items to cart
2. Click "Proceed to Checkout"
3. Login if not authenticated
4. Fill shipping address
5. Select payment method
6. Complete payment (use Stripe test cards)

**Stripe Test Cards**
- Success: `4242 4242 4242 4242`
- Declined: `4000 0000 0000 0002`
- Any future expiry, any 3-digit CVC

## Available Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Customer-facing store |
| Backend API | http://localhost:8000/api | REST API |
| API Docs | http://localhost:8000/api/swagger | Swagger documentation |
| Django Admin | http://localhost:8000/admin | Admin interface |
| MailHog UI | http://localhost:8025 | Email testing interface |

## Key Features Implemented

### Authentication
- ✅ User registration with email verification
- ✅ Login/logout with JWT tokens
- ✅ Password reset via email
- ✅ Protected routes

### Payments
- ✅ Stripe (credit/debit cards)
- ✅ MTN Mobile Money
- ✅ Airtel Money
- ✅ Payment tracking and history
- ✅ Webhook support
- ✅ Partial payments

### Orders
- ✅ Order creation from cart
- ✅ Order history page
- ✅ Order details with payment options
- ✅ Payment status tracking
- ✅ Fulfillment status tracking

## Common Issues

### Payment fails with "Gateway not available"
- Check that payment gateway is configured and `is_active=True`
- Verify API credentials are correct
- Check Django logs: `docker compose logs web -f`

### Email not sending
- Verify MailHog is running: `docker compose ps mailhog`
- Check email in MailHog UI: http://localhost:8025

### Frontend can't connect to backend
- Ensure backend is running: `docker compose ps web`
- Check `web/.env.local` has `VITE_API_BASE_URL=http://localhost:8000`
- Clear browser cache and restart frontend

### Database errors
- Run migrations: `docker compose exec web python manage.py migrate`
- Check database: `docker compose ps db`

## Development Commands

```bash
# Backend
docker compose up -d              # Start all services
docker compose logs web -f        # View backend logs
docker compose exec web python manage.py shell  # Django shell
docker compose down               # Stop all services

# Frontend
npm run dev:client                # Start frontend
npm run build:client              # Build for production

# Database
docker compose exec web python manage.py dbshell  # PostgreSQL shell
docker compose exec web python manage.py migrate # Run migrations
```

## Support & Documentation

- **Full Setup Guide**: [SETUP.md](./SETUP.md)
- **Django Admin**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/swagger

## What's Next?

1. **Configure Real Payment Gateways**: Update API keys with production credentials
2. **Test Payment Flows**: Test each payment method thoroughly
3. **Customize Email Templates**: Create branded email templates
4. **Add Product Reviews**: Implement the review system (models ready, UI pending)
5. **Deploy to Production**: Follow production deployment guide in SETUP.md

---

🎉 **Congratulations!** Your e-commerce platform with authentication and multi-payment gateway support is ready!
