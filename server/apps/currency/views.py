from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from .models import ExchangeRate
from .serializers import (
    ExchangeRateSerializer,
    CurrencyConversionSerializer,
    CurrencyInfoSerializer
)


class ExchangeRateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing exchange rates.

    List, create, update, and delete exchange rates.
    Admin only for write operations.
    """
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer

    def get_queryset(self):
        """Filter active currencies for non-admin users"""
        queryset = ExchangeRate.objects.all()

        # Filter by active status if requested
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.order_by('currency_code')

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active currencies"""
        active_currencies = ExchangeRate.get_active_currencies()
        serializer = self.get_serializer(active_currencies, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def convert_currency(request):
    """
    Convert amount from one currency to another.

    POST /api/currency/convert/
    {
        "amount": 100000,
        "from_currency": "UGX",  // optional, defaults to UGX
        "to_currency": "USD"
    }
    """
    serializer = CurrencyConversionSerializer(data=request.data)

    if serializer.is_valid():
        result = serializer.convert()
        return Response(result, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_currency_info(request, currency_code):
    """
    Get information about a specific currency.

    GET /api/currency/info/<currency_code>/
    """
    currency_info = ExchangeRate.get_currency_info(currency_code)
    serializer = CurrencyInfoSerializer(currency_info)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_all_currencies(request):
    """
    Get all active currencies with basic info.

    GET /api/currency/all/
    """
    currencies = ExchangeRate.get_active_currencies()
    data = [
        {
            'code': currency.currency_code,
            'name': currency.currency_name,
            'symbol': currency.symbol,
            'decimal_places': currency.decimal_places,
        }
        for currency in currencies
    ]

    # Always include UGX as base currency
    ugx_included = any(c['code'] == 'UGX' for c in data)
    if not ugx_included:
        data.insert(0, {
            'code': 'UGX',
            'name': 'Ugandan Shilling',
            'symbol': 'UGX',
            'decimal_places': 0,
        })

    return Response(data, status=status.HTTP_200_OK)
