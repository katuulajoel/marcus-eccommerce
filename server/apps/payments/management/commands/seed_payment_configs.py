"""
Django management command to seed payment gateway configurations
Run with: python manage.py seed_payment_configs
"""
import os
from django.core.management.base import BaseCommand
from apps.payments.models import PaymentGatewayConfig


class Command(BaseCommand):
    help = 'Seed payment gateway configurations from environment variables'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting payment gateway configuration seeding...')

        # Get environment variables
        stripe_api_key = os.getenv('STRIPE_API_KEY', '')
        stripe_api_secret = os.getenv('STRIPE_API_SECRET', '')
        mtn_api_key = os.getenv('MTN_API_KEY', '')
        mtn_api_secret = os.getenv('MTN_API_SECRET', '')
        airtel_api_key = os.getenv('AIRTEL_API_KEY', '')
        airtel_api_secret = os.getenv('AIRTEL_API_SECRET', '')

        # Determine environment (default to sandbox in development)
        payment_environment = os.getenv('PAYMENT_ENVIRONMENT', 'sandbox')

        gateway_configs = [
            {
                'gateway_name': 'stripe',
                'api_key': stripe_api_key,
                'api_secret': stripe_api_secret,
                'is_active': bool(stripe_api_key),  # Only active if key exists
                'environment': payment_environment,
                'webhook_secret': os.getenv('STRIPE_WEBHOOK_SECRET', ''),
                'additional_config': {
                    'currency': 'ugx',
                    'payment_methods': ['card'],
                }
            },
            {
                'gateway_name': 'mtn_momo',
                'api_key': mtn_api_key,
                'api_secret': mtn_api_secret,
                'is_active': bool(mtn_api_key),
                'environment': payment_environment,
                'webhook_secret': os.getenv('MTN_WEBHOOK_SECRET', ''),
                'additional_config': {
                    'currency': 'ugx',
                    'callback_url': os.getenv('MTN_CALLBACK_URL', ''),
                    'subscription_key': os.getenv('MTN_SUBSCRIPTION_KEY', ''),
                }
            },
            {
                'gateway_name': 'airtel_money',
                'api_key': airtel_api_key,
                'api_secret': airtel_api_secret,
                'is_active': bool(airtel_api_key),
                'environment': payment_environment,
                'webhook_secret': os.getenv('AIRTEL_WEBHOOK_SECRET', ''),
                'additional_config': {
                    'currency': 'ugx',
                    'callback_url': os.getenv('AIRTEL_CALLBACK_URL', ''),
                }
            },
        ]

        created_count = 0
        updated_count = 0

        for config_data in gateway_configs:
            gateway_name = config_data['gateway_name']

            # Get or create the config
            config, created = PaymentGatewayConfig.objects.update_or_create(
                gateway_name=gateway_name,
                defaults={
                    'api_key': config_data['api_key'],
                    'api_secret': config_data['api_secret'],
                    'is_active': config_data['is_active'],
                    'environment': config_data['environment'],
                    'webhook_secret': config_data['webhook_secret'],
                    'additional_config': config_data['additional_config'],
                }
            )

            if created:
                created_count += 1
                status = "✅ Created"
            else:
                updated_count += 1
                status = "🔄 Updated"

            active_status = "🟢 Active" if config.is_active else "🔴 Inactive"
            self.stdout.write(f"  {status}: {config.get_gateway_name_display()} ({config.environment}) {active_status}")

        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("✅ Payment gateway configuration seeding completed!"))
        self.stdout.write("="*60)
        self.stdout.write(f"📊 Summary:")
        self.stdout.write(f"   - Created: {created_count}")
        self.stdout.write(f"   - Updated: {updated_count}")
        self.stdout.write(f"   - Total configs: {PaymentGatewayConfig.objects.count()}")
        self.stdout.write(f"   - Active gateways: {PaymentGatewayConfig.objects.filter(is_active=True).count()}")
        self.stdout.write("="*60)

        # Show warning if no keys are configured
        if not any([stripe_api_key, mtn_api_key, airtel_api_key]):
            self.stdout.write(self.style.WARNING("\n⚠️  WARNING: No payment gateway API keys found in environment variables!"))
            self.stdout.write("   Add the following to your .env file:")
            self.stdout.write("   - STRIPE_API_KEY=your_stripe_key")
            self.stdout.write("   - STRIPE_API_SECRET=your_stripe_secret")
            self.stdout.write("   - MTN_API_KEY=your_mtn_key")
            self.stdout.write("   - MTN_API_SECRET=your_mtn_secret")
            self.stdout.write("   - AIRTEL_API_KEY=your_airtel_key")
            self.stdout.write("   - AIRTEL_API_SECRET=your_airtel_secret")
