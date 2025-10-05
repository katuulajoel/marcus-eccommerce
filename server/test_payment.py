#!/usr/bin/env python
"""
Quick test script for payment gateway integration
Run with: docker compose exec web python test_payment.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()

from decimal import Decimal
from apps.payments.services import PaymentService
from apps.payments.models import PaymentGatewayConfig

def test_stripe_gateway():
    """Test Stripe gateway initialization"""
    print("\n" + "="*60)
    print("Testing Stripe Gateway")
    print("="*60)

    try:
        # Check if Stripe is configured
        config = PaymentGatewayConfig.objects.get(gateway_name='stripe')
        print(f"✓ Stripe gateway configured: {config.environment}")
        print(f"  API Key: {config.api_key[:20]}..." if config.api_key else "  No API Key")

        # Get gateway instance
        gateway = PaymentService.get_gateway('stripe')
        if gateway:
            print("✓ Stripe gateway instance created successfully")

            # Test payment initialization (won't work with placeholder keys)
            result = gateway.initialize_payment(
                amount=Decimal('100.00'),
                currency='USD',
                order_id=999,
                customer_data={
                    'email': 'test@example.com',
                    'name': 'Test User',
                    'phone': '+256700000000'
                }
            )

            if result.success:
                print("✓ Payment initialization successful!")
                print(f"  Transaction ID: {result.transaction_id}")
                print(f"  Status: {result.status}")
            else:
                print(f"✗ Payment initialization failed: {result.error}")
                if "API key" in result.error or "Invalid" in result.error:
                    print("\n💡 This is expected with placeholder API keys")
                    print("   Update your Stripe API keys in Django admin:")
                    print("   http://localhost:8000/admin/payments/paymentgatewayconfig/")
        else:
            print("✗ Failed to get Stripe gateway instance")

    except PaymentGatewayConfig.DoesNotExist:
        print("✗ Stripe gateway not configured")
        print("  Run setup script to configure payment gateways")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_mtn_momo_gateway():
    """Test MTN MoMo gateway"""
    print("\n" + "="*60)
    print("Testing MTN MoMo Gateway")
    print("="*60)

    try:
        config = PaymentGatewayConfig.objects.get(gateway_name='mtn_momo')
        print(f"✓ MTN MoMo gateway configured: {config.environment}")

        gateway = PaymentService.get_gateway('mtn_momo')
        if gateway:
            print("✓ MTN MoMo gateway instance created successfully")
        else:
            print("✗ Failed to get MTN MoMo gateway instance")

    except PaymentGatewayConfig.DoesNotExist:
        print("✗ MTN MoMo gateway not configured")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_airtel_gateway():
    """Test Airtel Money gateway"""
    print("\n" + "="*60)
    print("Testing Airtel Money Gateway")
    print("="*60)

    try:
        config = PaymentGatewayConfig.objects.get(gateway_name='airtel_money')
        print(f"✓ Airtel Money gateway configured: {config.environment}")

        gateway = PaymentService.get_gateway('airtel_money')
        if gateway:
            print("✓ Airtel Money gateway instance created successfully")
        else:
            print("✗ Failed to get Airtel Money gateway instance")

    except PaymentGatewayConfig.DoesNotExist:
        print("✗ Airtel Money gateway not configured")
    except Exception as e:
        print(f"✗ Error: {e}")

def list_available_gateways():
    """List all available payment gateways"""
    print("\n" + "="*60)
    print("Available Payment Gateways")
    print("="*60)

    gateways = PaymentGatewayConfig.objects.all()
    if gateways:
        for gateway in gateways:
            status = "✓ Active" if gateway.is_active else "✗ Inactive"
            print(f"{status}: {gateway.get_gateway_name_display()} ({gateway.environment})")
    else:
        print("No payment gateways configured")

if __name__ == "__main__":
    print("\n🔧 Payment Gateway Test Suite")
    print("="*60)

    list_available_gateways()
    test_stripe_gateway()
    test_mtn_momo_gateway()
    test_airtel_gateway()

    print("\n" + "="*60)
    print("✅ Test complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update payment gateway API keys in Django admin")
    print("2. Test payment flow through the frontend")
    print("3. Check logs: docker compose logs web -f")
    print()
