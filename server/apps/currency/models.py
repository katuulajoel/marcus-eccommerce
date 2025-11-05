from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone


class ExchangeRate(models.Model):
    """
    Exchange rates for currency conversion.

    Base currency is UGX (Ugandan Shilling).
    Rates represent: 1 USD = X UGX, 1 GBP = X UGX, etc.
    """
    # Currency code (ISO 4217)
    currency_code = models.CharField(
        max_length=3,
        unique=True,
        help_text="ISO 4217 currency code (e.g., USD, GBP, KES)"
    )

    # Currency name
    currency_name = models.CharField(
        max_length=100,
        help_text="Full currency name (e.g., US Dollar, British Pound)"
    )

    # Exchange rate to UGX
    rate_to_ugx = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        help_text="Exchange rate: 1 [Currency] = X UGX"
    )

    # Symbol
    symbol = models.CharField(
        max_length=10,
        help_text="Currency symbol (e.g., $, £, €)"
    )

    # Decimal places
    decimal_places = models.IntegerField(
        default=2,
        help_text="Number of decimal places for this currency"
    )

    # Is active
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this currency is currently available for selection"
    )

    # Rate source
    RATE_SOURCE_CHOICES = [
        ('manual', 'Manual'),
        ('api', 'API'),
    ]
    rate_source = models.CharField(
        max_length=10,
        choices=RATE_SOURCE_CHOICES,
        default='manual',
        help_text="How this rate was set"
    )

    # Last updated
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="When the rate was last updated"
    )

    # Created at
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exchange_rate'
        ordering = ['currency_code']
        verbose_name = 'Exchange Rate'
        verbose_name_plural = 'Exchange Rates'

    def __str__(self):
        return f"1 {self.currency_code} = {self.rate_to_ugx} UGX"

    def get_rate_from_ugx(self):
        """Get the inverse rate: 1 UGX = X [Currency]"""
        return Decimal('1.00') / self.rate_to_ugx if self.rate_to_ugx > 0 else Decimal('0')

    @classmethod
    def convert(cls, amount, from_currency='UGX', to_currency='UGX'):
        """
        Convert amount from one currency to another.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Converted amount
        """
        if from_currency == to_currency:
            return amount

        # If converting from UGX
        if from_currency == 'UGX':
            try:
                rate = cls.objects.get(currency_code=to_currency, is_active=True)
                return (amount / rate.rate_to_ugx).quantize(
                    Decimal('0.01') if rate.decimal_places == 2 else Decimal('1')
                )
            except cls.DoesNotExist:
                return amount

        # If converting to UGX
        elif to_currency == 'UGX':
            try:
                rate = cls.objects.get(currency_code=from_currency, is_active=True)
                return (amount * rate.rate_to_ugx).quantize(Decimal('1'))
            except cls.DoesNotExist:
                return amount

        # If converting between two non-UGX currencies
        else:
            # Convert to UGX first, then to target currency
            try:
                from_rate = cls.objects.get(currency_code=from_currency, is_active=True)
                to_rate = cls.objects.get(currency_code=to_currency, is_active=True)

                amount_in_ugx = amount * from_rate.rate_to_ugx
                converted = amount_in_ugx / to_rate.rate_to_ugx

                return converted.quantize(
                    Decimal('0.01') if to_rate.decimal_places == 2 else Decimal('1')
                )
            except cls.DoesNotExist:
                return amount

    @classmethod
    def get_active_currencies(cls):
        """Get all active currencies"""
        return cls.objects.filter(is_active=True).order_by('currency_code')

    @classmethod
    def get_currency_info(cls, currency_code):
        """Get currency information"""
        try:
            rate = cls.objects.get(currency_code=currency_code, is_active=True)
            return {
                'code': rate.currency_code,
                'name': rate.currency_name,
                'symbol': rate.symbol,
                'decimal_places': rate.decimal_places,
                'rate_to_ugx': float(rate.rate_to_ugx),
                'last_updated': rate.last_updated.isoformat(),
            }
        except cls.DoesNotExist:
            # Return UGX default
            return {
                'code': 'UGX',
                'name': 'Ugandan Shilling',
                'symbol': 'UGX',
                'decimal_places': 0,
                'rate_to_ugx': 1.0,
                'last_updated': timezone.now().isoformat(),
            }
