"""
Currency configuration API endpoint
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .currency_config import CurrencyConfig


@api_view(['GET'])
@permission_classes([AllowAny])
def currency_config(request):
    """
    Get currency configuration for the frontend.

    Returns:
        {
            "default_currency": "UGX",
            "symbol": "UGX",
            "name": "Ugandan Shilling",
            "decimal_places": 0,
            "thousand_separator": ",",
            "decimal_separator": ".",
            "display_format": "UGX {amount}"
        }
    """
    return Response(CurrencyConfig.get_config())
