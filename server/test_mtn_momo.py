#!/usr/bin/env python3
"""
Test MTN MoMo payment gateway
Reads configuration from database

Run with: docker compose exec web python test_mtn_momo.py
"""

import django
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from apps.payments.gateways.mtn_momo import MTNMoMoGateway
from apps.payments.models import PaymentGatewayConfig

# Get MTN MoMo config from database
try:
    gateway_config = PaymentGatewayConfig.objects.get(gateway_name='mtn_momo', is_active=True)

    # Build config from database fields
    config = {
        'api_secret': gateway_config.api_secret,
        'environment': gateway_config.environment,
        **gateway_config.additional_config  # Merge any additional configs (api_user, api_key, callback_url, etc.)
    }

    print(f"✓ Loaded MTN MoMo config from database (ID: {gateway_config.id})")
except PaymentGatewayConfig.DoesNotExist:
    print("✗ No active MTN MoMo gateway config found in database")
    print("  Please create a PaymentGatewayConfig with gateway_name='mtn_momo'")
    sys.exit(1)

print("=" * 60)
print("MTN MoMo Gateway Test")
print("=" * 60)

# Initialize gateway (will create API user/key if not provided)
gateway = MTNMoMoGateway(config)

print(f"\n✓ Gateway initialized")
if gateway.api_user:
    print(f"  API User: {gateway.api_user}")
if gateway.api_key:
    print(f"  API Key: {gateway.api_key[:8]}...")
if gateway.subscription_key:
    print(f"  Subscription Key: {gateway.subscription_key[:8]}...")

# Test payment initialization (same as your step 6)
print(f"\n{'='*60}")
print("Testing Payment Initialization")
print("=" * 60)

# Test with exact same parameters as working Postman request
result = gateway.initialize_payment(
    amount=Decimal('1420.00'),
    currency='EUR',
    order_id=3,
    customer_data={
        'phone': '0781856352',  # Uganda test number
        'email': 'test@example.com',
        'name': 'Test Customer'
    },
    metadata={
        'payerMessage': 'Pay for product a',  # Match working request
        'payeeNote': 'payer note'  # Match working request
    }
)

print(f"\nPayment Initialization Result:")
print(f"  Success: {result.success}")
print(f"  Status: {result.status}")
print(f"  Transaction ID: {result.transaction_id}")
print(f"  Message: {result.message}")
print(f"  Requires Action: {result.requires_action}")

if result.raw_response:
    print(f"  Raw Response: {result.raw_response}")

if result.error:
    print(f"  ✗ Error: {result.error}")

# If successful, verify payment status
if result.success and result.transaction_id:
    print(f"\n{'='*60}")
    print("Testing Payment Verification")
    print("=" * 60)

    verification = gateway.verify_payment(result.transaction_id)

    print(f"\nPayment Verification Result:")
    print(f"  Success: {verification.success}")
    print(f"  Status: {verification.status}")
    print(f"  Message: {verification.message}")

    if verification.raw_response:
        print(f"  Raw Response: {verification.raw_response}")

    if verification.error:
        print(f"  ✗ Error: {verification.error}")

print(f"\n{'='*60}")
print("Test Complete")
print("=" * 60)
