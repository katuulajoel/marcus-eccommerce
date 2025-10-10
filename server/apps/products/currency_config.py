"""
Currency configuration for the e-commerce system.

This module provides currency configuration that can be easily changed
for different deployments or regions.
"""

from decimal import Decimal
from typing import Dict, Any


class CurrencyConfig:
    """
    Centralized currency configuration.

    To change currency for a different deployment:
    1. Update DEFAULT_CURRENCY
    2. Update CURRENCY_SYMBOL
    3. Adjust CONVERSION_RATES if needed
    4. Update CURRENCY_DISPLAY_FORMAT
    """

    # Default currency for the system
    DEFAULT_CURRENCY = "UGX"  # Change this for different countries

    # Currency symbols
    CURRENCY_SYMBOLS = {
        "UGX": "UGX",
        "USD": "$",
        "KES": "KSh",
        "TZS": "TSh",
        "RWF": "RWF",
        "EUR": "€",
        "GBP": "£",
    }

    # Currency display names
    CURRENCY_NAMES = {
        "UGX": "Ugandan Shilling",
        "USD": "US Dollar",
        "KES": "Kenyan Shilling",
        "TZS": "Tanzanian Shilling",
        "RWF": "Rwandan Franc",
        "EUR": "Euro",
        "GBP": "British Pound",
    }

    # Number of decimal places for each currency
    DECIMAL_PLACES = {
        "UGX": 0,  # UGX typically doesn't use decimals
        "USD": 2,
        "KES": 2,
        "TZS": 0,
        "RWF": 0,
        "EUR": 2,
        "GBP": 2,
    }

    # Thousand separators
    THOUSAND_SEPARATOR = {
        "UGX": ",",
        "USD": ",",
        "KES": ",",
        "TZS": ",",
        "RWF": ",",
        "EUR": ".",
        "GBP": ",",
    }

    # Decimal separators
    DECIMAL_SEPARATOR = {
        "UGX": ".",
        "USD": ".",
        "KES": ".",
        "TZS": ".",
        "RWF": ".",
        "EUR": ",",
        "GBP": ".",
    }

    # Currency formatting patterns
    # {symbol} = currency symbol, {amount} = formatted amount
    DISPLAY_FORMAT = {
        "UGX": "UGX {amount}",  # e.g., "UGX 10,000"
        "USD": "${amount}",      # e.g., "$100.00"
        "KES": "KSh {amount}",   # e.g., "KSh 1,000"
        "TZS": "TSh {amount}",
        "RWF": "RWF {amount}",
        "EUR": "€{amount}",
        "GBP": "£{amount}",
    }

    # Conversion rates (relative to USD)
    # Update these for real-time conversion or use an API
    CONVERSION_RATES = {
        "UGX": Decimal("3700.00"),  # 1 USD = 3700 UGX (example rate)
        "USD": Decimal("1.00"),
        "KES": Decimal("150.00"),
        "TZS": Decimal("2500.00"),
        "RWF": Decimal("1300.00"),
        "EUR": Decimal("0.92"),
        "GBP": Decimal("0.79"),
    }

    @classmethod
    def get_symbol(cls, currency: str = None) -> str:
        """Get currency symbol"""
        currency = currency or cls.DEFAULT_CURRENCY
        return cls.CURRENCY_SYMBOLS.get(currency, currency)

    @classmethod
    def get_decimal_places(cls, currency: str = None) -> int:
        """Get number of decimal places for currency"""
        currency = currency or cls.DEFAULT_CURRENCY
        return cls.DECIMAL_PLACES.get(currency, 2)

    @classmethod
    def format_amount(cls, amount: Decimal, currency: str = None, include_symbol: bool = True) -> str:
        """
        Format amount according to currency rules.

        Args:
            amount: Amount to format
            currency: Currency code (defaults to DEFAULT_CURRENCY)
            include_symbol: Whether to include currency symbol

        Returns:
            Formatted currency string
        """
        currency = currency or cls.DEFAULT_CURRENCY
        decimal_places = cls.get_decimal_places(currency)

        # Round to appropriate decimal places
        if decimal_places == 0:
            rounded_amount = int(round(amount))
            formatted = f"{rounded_amount:,}"
        else:
            rounded_amount = round(amount, decimal_places)
            formatted = f"{rounded_amount:,.{decimal_places}f}"

        # Apply currency-specific separators
        thousand_sep = cls.THOUSAND_SEPARATOR.get(currency, ",")
        decimal_sep = cls.DECIMAL_SEPARATOR.get(currency, ".")

        # Replace separators if different from default
        if thousand_sep != ",":
            formatted = formatted.replace(",", "TEMP")
            formatted = formatted.replace(".", decimal_sep)
            formatted = formatted.replace("TEMP", thousand_sep)
        elif decimal_sep != ".":
            formatted = formatted.replace(".", decimal_sep)

        if not include_symbol:
            return formatted

        # Apply display format
        display_format = cls.DISPLAY_FORMAT.get(currency, "{symbol} {amount}")
        symbol = cls.get_symbol(currency)

        return display_format.format(symbol=symbol, amount=formatted)

    @classmethod
    def convert(cls, amount: Decimal, from_currency: str, to_currency: str = None) -> Decimal:
        """
        Convert amount from one currency to another.

        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency (defaults to DEFAULT_CURRENCY)

        Returns:
            Converted amount
        """
        to_currency = to_currency or cls.DEFAULT_CURRENCY

        if from_currency == to_currency:
            return amount

        # Convert to USD first, then to target currency
        from_rate = cls.CONVERSION_RATES.get(from_currency, Decimal("1.00"))
        to_rate = cls.CONVERSION_RATES.get(to_currency, Decimal("1.00"))

        amount_in_usd = amount / from_rate
        converted_amount = amount_in_usd * to_rate

        return converted_amount.quantize(Decimal("0.01"))

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get currency configuration as dictionary (for API responses)"""
        return {
            "default_currency": cls.DEFAULT_CURRENCY,
            "symbol": cls.get_symbol(),
            "name": cls.CURRENCY_NAMES.get(cls.DEFAULT_CURRENCY, cls.DEFAULT_CURRENCY),
            "decimal_places": cls.get_decimal_places(),
            "thousand_separator": cls.THOUSAND_SEPARATOR.get(cls.DEFAULT_CURRENCY, ","),
            "decimal_separator": cls.DECIMAL_SEPARATOR.get(cls.DEFAULT_CURRENCY, "."),
            "display_format": cls.DISPLAY_FORMAT.get(cls.DEFAULT_CURRENCY, "{symbol} {amount}"),
        }


# Convenience function for quick formatting
def format_currency(amount: Decimal, currency: str = None, include_symbol: bool = True) -> str:
    """Format amount as currency string"""
    return CurrencyConfig.format_amount(amount, currency, include_symbol)
