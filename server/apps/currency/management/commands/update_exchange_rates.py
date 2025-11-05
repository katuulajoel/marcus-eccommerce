from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.currency.models import ExchangeRate
from decimal import Decimal
import requests


class Command(BaseCommand):
    help = 'Update exchange rates from external API or manually set rates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--manual',
            action='store_true',
            help='Skip API call and use manual rates defined in command',
        )
        parser.add_argument(
            '--currency',
            type=str,
            help='Update specific currency only (e.g., USD)',
        )

    def handle(self, *args, **options):
        """Update exchange rates"""
        if options['manual']:
            self.update_manual_rates(options.get('currency'))
        else:
            self.update_from_api(options.get('currency'))

    def update_manual_rates(self, currency_code=None):
        """
        Update rates manually with predefined values.
        These are approximate rates - update these values as needed.
        """
        self.stdout.write('Updating exchange rates manually...')

        # Manual rates: 1 CURRENCY = X UGX
        manual_rates = {
            'USD': {
                'rate': Decimal('3700.0000'),
                'name': 'US Dollar',
                'symbol': '$',
                'decimal_places': 2,
            },
            'GBP': {
                'rate': Decimal('4650.0000'),
                'name': 'British Pound',
                'symbol': '£',
                'decimal_places': 2,
            },
            'EUR': {
                'rate': Decimal('4000.0000'),
                'name': 'Euro',
                'symbol': '€',
                'decimal_places': 2,
            },
            'KES': {
                'rate': Decimal('28.5000'),
                'name': 'Kenyan Shilling',
                'symbol': 'KSh',
                'decimal_places': 2,
            },
            'TZS': {
                'rate': Decimal('1.5500'),
                'name': 'Tanzanian Shilling',
                'symbol': 'TSh',
                'decimal_places': 2,
            },
        }

        # Filter to specific currency if requested
        if currency_code:
            if currency_code.upper() in manual_rates:
                manual_rates = {currency_code.upper(): manual_rates[currency_code.upper()]}
            else:
                self.stdout.write(
                    self.style.ERROR(f'Currency {currency_code} not found in manual rates')
                )
                return

        # Update or create each currency
        for code, data in manual_rates.items():
            rate, created = ExchangeRate.objects.update_or_create(
                currency_code=code,
                defaults={
                    'currency_name': data['name'],
                    'rate_to_ugx': data['rate'],
                    'symbol': data['symbol'],
                    'decimal_places': data['decimal_places'],
                    'is_active': True,
                    'rate_source': 'manual',
                }
            )

            action = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(
                    f'{action} {code}: 1 {code} = {data["rate"]} UGX'
                )
            )

        self.stdout.write(self.style.SUCCESS('Manual rate update completed'))

    def update_from_api(self, currency_code=None):
        """
        Update rates from exchangerate-api.com API.
        Fetches real-time exchange rates with UGX as base currency.
        """
        from django.conf import settings

        self.stdout.write('Fetching exchange rates from API...')

        try:
            # Get API key from settings
            api_key = settings.EXCHANGE_RATE_API_KEY
            base_url = f'{settings.EXCHANGE_RATE_API_BASE_URL}/{api_key}/latest/UGX'

            # Make API request
            response = requests.get(base_url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Check if request was successful
            if data.get('result') != 'success':
                raise Exception(f"API returned error: {data.get('error-type', 'Unknown error')}")

            rates = data['conversion_rates']
            self.stdout.write(f'Received {len(rates)} exchange rates from API')

            # Currency metadata (name, symbol, decimal places)
            currency_metadata = {
                'USD': {'name': 'US Dollar', 'symbol': '$', 'decimal_places': 2},
                'GBP': {'name': 'British Pound', 'symbol': '£', 'decimal_places': 2},
                'EUR': {'name': 'Euro', 'symbol': '€', 'decimal_places': 2},
                'KES': {'name': 'Kenyan Shilling', 'symbol': 'KSh', 'decimal_places': 2},
                'TZS': {'name': 'Tanzanian Shilling', 'symbol': 'TSh', 'decimal_places': 2},
                'ZAR': {'name': 'South African Rand', 'symbol': 'R', 'decimal_places': 2},
                'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'decimal_places': 0},
                'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'decimal_places': 2},
                'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'decimal_places': 2},
                'AUD': {'name': 'Australian Dollar', 'symbol': 'A$', 'decimal_places': 2},
                'CAD': {'name': 'Canadian Dollar', 'symbol': 'C$', 'decimal_places': 2},
            }

            # Filter to only update currencies we care about
            target_currencies = ['USD', 'GBP', 'EUR', 'KES', 'TZS', 'ZAR', 'JPY', 'CNY', 'INR', 'AUD', 'CAD']

            if currency_code:
                # If specific currency requested, only update that one
                target_currencies = [currency_code.upper()]

            updated_count = 0
            for code in target_currencies:
                if code not in rates:
                    self.stdout.write(self.style.WARNING(f'Currency {code} not found in API response'))
                    continue

                rate_from_ugx = rates[code]

                # Convert to rate_to_ugx (inverse)
                # API gives us: 1 UGX = X [currency]
                # We need: 1 [currency] = Y UGX
                rate_to_ugx = Decimal('1') / Decimal(str(rate_from_ugx))

                # Get metadata or use defaults
                metadata = currency_metadata.get(code, {
                    'name': code,
                    'symbol': code,
                    'decimal_places': 2
                })

                # Update or create exchange rate
                rate_obj, created = ExchangeRate.objects.update_or_create(
                    currency_code=code,
                    defaults={
                        'currency_name': metadata['name'],
                        'rate_to_ugx': rate_to_ugx,
                        'symbol': metadata['symbol'],
                        'decimal_places': metadata['decimal_places'],
                        'is_active': True,
                        'rate_source': 'api',
                    }
                )

                action = 'Created' if created else 'Updated'
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{action} {code}: 1 {code} = {rate_to_ugx:.4f} UGX (1 UGX = {rate_from_ugx:.6f} {code})'
                    )
                )
                updated_count += 1

            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully updated {updated_count} exchange rates from API'))

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'API request failed: {e}'))
            self.stdout.write(self.style.WARNING('Falling back to manual rates...'))
            self.update_manual_rates(currency_code)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating exchange rates: {e}'))
            self.stdout.write(self.style.WARNING('Falling back to manual rates...'))
            self.update_manual_rates(currency_code)
