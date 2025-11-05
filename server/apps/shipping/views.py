from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import ShippingConstants, ShippingZone, ZoneArea, ShippingRate, OrderShippingMethod
from .serializers import (
    ShippingConstantsSerializer, ShippingZoneSerializer, ZoneAreaSerializer,
    ShippingRateSerializer, OrderShippingMethodSerializer,
    CalculateShippingRequestSerializer, MatchZoneRequestSerializer,
    ZoneSuggestionSerializer, ShippingZoneListSerializer
)
from .services import get_shipping_options, match_address_to_zone, get_zone_suggestions


class ShippingConstantsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for shipping constants (read-only for customers, admin can edit via Django admin)
    """
    queryset = ShippingConstants.objects.all()
    serializer_class = ShippingConstantsSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        """Return the singleton instance"""
        instance = ShippingConstants.get_instance()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ShippingZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for shipping zones (read-only for customers)

    list: Get all active shipping zones
    retrieve: Get details of a specific zone including areas
    """
    queryset = ShippingZone.objects.filter(is_active=True).prefetch_related('areas')
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return ShippingZoneListSerializer
        return ShippingZoneSerializer

    @action(detail=True, methods=['get'])
    def areas(self, request, pk=None):
        """Get all areas for a specific zone"""
        zone = self.get_object()
        areas = zone.areas.all()
        serializer = ZoneAreaSerializer(areas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def match(self, request):
        """
        Match an address to a shipping zone

        POST /api/shipping/zones/match/
        Body: {"address": "Ntinda, Kampala", "city": "Kampala"}
        """
        serializer = MatchZoneRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        address = serializer.validated_data['address']
        city = serializer.validated_data.get('city')

        matched_zone = match_address_to_zone(address, city)

        if matched_zone:
            zone_serializer = ShippingZoneSerializer(matched_zone)
            return Response({
                'matched': True,
                'zone': zone_serializer.data
            })
        else:
            return Response({
                'matched': False,
                'message': 'No zone found for this address. Please select manually.',
                'suggestions': []
            })

    @action(detail=False, methods=['get'])
    def suggest(self, request):
        """
        Get zone area suggestions for autocomplete

        GET /api/shipping/zones/suggest/?q=ntin
        """
        query = request.query_params.get('q', '')

        if len(query) < 2:
            return Response({
                'suggestions': []
            })

        suggestions = get_zone_suggestions(query)
        serializer = ZoneSuggestionSerializer(suggestions, many=True)

        return Response({
            'suggestions': serializer.data
        })


class ShippingRateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for shipping rates (read-only for customers)
    """
    queryset = ShippingRate.objects.filter(is_active=True).select_related('zone')
    serializer_class = ShippingRateSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by zone if provided
        zone_id = self.request.query_params.get('zone_id')
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)

        # Filter by delivery method if provided
        method = self.request.query_params.get('method')
        if method:
            queryset = queryset.filter(delivery_method=method)

        return queryset


class ShippingCalculatorViewSet(viewsets.ViewSet):
    """
    API endpoint for calculating shipping costs
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """
        Calculate shipping options for a cart

        POST /api/shipping/calculate/
        Body: {
            "cart_items": [
                {"category_id": 1, "quantity": 2},
                {"category_id": 3, "quantity": 1}
            ],
            "zone_id": 1
        }
        """
        serializer = CalculateShippingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_items = serializer.validated_data['cart_items']
        zone = serializer.validated_data['zone_id']

        try:
            shipping_options = get_shipping_options(cart_items, zone)

            return Response({
                'zone': {
                    'id': zone.id,
                    'zone_code': zone.zone_code,
                    'zone_name': zone.zone_name,
                },
                'shipping_options': shipping_options
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class OrderShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing order shipping methods (read-only)
    """
    queryset = OrderShippingMethod.objects.all().select_related('zone', 'rate', 'order')
    serializer_class = OrderShippingMethodSerializer
    permission_classes = [AllowAny]  # Will be restricted by order permissions

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by order if provided
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)

        return queryset
