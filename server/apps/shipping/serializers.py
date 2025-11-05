from rest_framework import serializers
from .models import ShippingConstants, ShippingZone, ZoneArea, ShippingRate, OrderShippingMethod


class ShippingConstantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingConstants
        fields = '__all__'


class ZoneAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZoneArea
        fields = ['id', 'area_name', 'is_landmark', 'keywords']


class ShippingZoneSerializer(serializers.ModelSerializer):
    areas = ZoneAreaSerializer(many=True, read_only=True)
    area_count = serializers.SerializerMethodField()

    class Meta:
        model = ShippingZone
        fields = [
            'id', 'zone_code', 'zone_name', 'distance_range_min_km',
            'distance_range_max_km', 'standard_delivery_days',
            'express_delivery_days', 'description', 'is_active',
            'areas', 'area_count'
        ]

    def get_area_count(self, obj):
        return obj.areas.count()


class ShippingZoneListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing zones without nested areas"""
    class Meta:
        model = ShippingZone
        fields = [
            'id', 'zone_code', 'zone_name', 'distance_range_min_km',
            'distance_range_max_km', 'standard_delivery_days',
            'express_delivery_days', 'is_active'
        ]


class ShippingRateSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.zone_name', read_only=True)
    delivery_method_display = serializers.CharField(source='get_delivery_method_display', read_only=True)
    service_level_display = serializers.CharField(source='get_service_level_display', read_only=True)

    class Meta:
        model = ShippingRate
        fields = [
            'id', 'zone', 'zone_name', 'delivery_method',
            'delivery_method_display', 'service_level',
            'service_level_display', 'base_price_ugx',
            'per_km_price_ugx', 'min_delivery_hours',
            'max_delivery_hours', 'is_active'
        ]


class OrderShippingMethodSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.zone_name', read_only=True)
    delivery_method_display = serializers.CharField(source='get_delivery_method_display', read_only=True)
    service_level_display = serializers.CharField(source='get_service_level_display', read_only=True)

    class Meta:
        model = OrderShippingMethod
        fields = [
            'id', 'order', 'zone', 'zone_name', 'delivery_method',
            'delivery_method_display', 'service_level',
            'service_level_display', 'base_shipping_cost_ugx',
            'helper_fee_ugx', 'extra_care_fee_ugx',
            'total_shipping_cost_ugx', 'total_weight_kg',
            'total_volume_m3', 'calculation_notes',
            'estimated_delivery_date', 'created_at'
        ]
        read_only_fields = ['total_shipping_cost_ugx', 'created_at']


class CalculateShippingRequestSerializer(serializers.Serializer):
    """Serializer for shipping calculation request"""
    cart_items = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of cart items with category_id and quantity"
    )
    zone_id = serializers.IntegerField(help_text="Shipping zone ID")

    def validate_cart_items(self, value):
        """Validate cart items structure"""
        from apps.products.models import Category

        if not value:
            raise serializers.ValidationError("Cart cannot be empty")

        validated_items = []
        for item in value:
            if 'category_id' not in item:
                raise serializers.ValidationError("Each item must have category_id")
            if 'quantity' not in item:
                raise serializers.ValidationError("Each item must have quantity")

            try:
                category = Category.objects.get(id=item['category_id'])
                validated_items.append({
                    'category': category,
                    'quantity': int(item['quantity'])
                })
            except Category.DoesNotExist:
                raise serializers.ValidationError(f"Category {item['category_id']} not found")
            except ValueError:
                raise serializers.ValidationError("Quantity must be a valid integer")

        return validated_items

    def validate_zone_id(self, value):
        """Validate zone exists and is active"""
        try:
            zone = ShippingZone.objects.get(id=value, is_active=True)
            return zone
        except ShippingZone.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive shipping zone")


class MatchZoneRequestSerializer(serializers.Serializer):
    """Serializer for zone matching request"""
    address = serializers.CharField(max_length=500)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)


class ZoneSuggestionSerializer(serializers.Serializer):
    """Serializer for zone area suggestions"""
    area_name = serializers.CharField()
    zone_id = serializers.IntegerField()
    zone_code = serializers.CharField()
    zone_name = serializers.CharField()
    is_landmark = serializers.BooleanField()
