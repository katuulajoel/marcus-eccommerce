from django.contrib import admin
from .models import ShippingConstants, ShippingZone, ZoneArea, ShippingRate, OrderShippingMethod


class ZoneAreaInline(admin.TabularInline):
    model = ZoneArea
    extra = 1
    fields = ['area_name', 'is_landmark', 'keywords']


@admin.register(ShippingConstants)
class ShippingConstantsAdmin(admin.ModelAdmin):
    list_display = ['id', 'boda_max_weight_kg', 'helper_fee_ugx', 'extra_care_fee_ugx']
    fieldsets = (
        ('Boda Boda Limits', {
            'fields': ('boda_max_weight_kg', 'boda_max_length_cm', 'boda_max_width_cm', 'boda_max_height_cm')
        }),
        ('Van/Pickup Limits', {
            'fields': ('van_max_weight_kg', 'van_max_length_cm', 'van_max_width_cm', 'van_max_height_cm')
        }),
        ('Truck Limits', {
            'fields': ('truck_max_weight_kg',)
        }),
        ('Additional Fees (UGX)', {
            'fields': ('helper_fee_ugx', 'extra_care_fee_ugx')
        }),
    )

    def has_add_permission(self, request):
        # Singleton - only one instance allowed
        return not ShippingConstants.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Cannot delete the singleton
        return False


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ['zone_code', 'zone_name', 'distance_range_min_km', 'distance_range_max_km', 'standard_delivery_days', 'is_active']
    list_filter = ['is_active']
    search_fields = ['zone_code', 'zone_name']
    inlines = [ZoneAreaInline]
    fieldsets = (
        ('Zone Information', {
            'fields': ('zone_code', 'zone_name', 'description', 'is_active')
        }),
        ('Distance Range (km)', {
            'fields': ('distance_range_min_km', 'distance_range_max_km')
        }),
        ('Delivery Times', {
            'fields': ('standard_delivery_days', 'express_delivery_days')
        }),
    )


@admin.register(ZoneArea)
class ZoneAreaAdmin(admin.ModelAdmin):
    list_display = ['area_name', 'zone', 'is_landmark']
    list_filter = ['zone', 'is_landmark']
    search_fields = ['area_name', 'keywords']
    fields = ['zone', 'area_name', 'is_landmark', 'keywords']


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ['zone', 'delivery_method', 'service_level', 'base_price_ugx', 'per_km_price_ugx', 'is_active']
    list_filter = ['zone', 'delivery_method', 'service_level', 'is_active']
    search_fields = ['zone__zone_name', 'zone__zone_code']
    fieldsets = (
        ('Rate Configuration', {
            'fields': ('zone', 'delivery_method', 'service_level', 'is_active')
        }),
        ('Pricing (UGX)', {
            'fields': ('base_price_ugx', 'per_km_price_ugx')
        }),
        ('Delivery Time', {
            'fields': ('min_delivery_hours', 'max_delivery_hours')
        }),
    )


@admin.register(OrderShippingMethod)
class OrderShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['order', 'zone', 'delivery_method', 'service_level', 'total_shipping_cost_ugx', 'estimated_delivery_date']
    list_filter = ['delivery_method', 'service_level', 'zone']
    search_fields = ['order__id', 'zone__zone_name']
    readonly_fields = ['order', 'total_shipping_cost_ugx', 'created_at', 'updated_at']
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'zone', 'rate')
        }),
        ('Shipping Method', {
            'fields': ('delivery_method', 'service_level')
        }),
        ('Costs (UGX)', {
            'fields': ('base_shipping_cost_ugx', 'helper_fee_ugx', 'extra_care_fee_ugx', 'total_shipping_cost_ugx')
        }),
        ('Shipment Details', {
            'fields': ('total_weight_kg', 'total_volume_m3', 'calculation_notes')
        }),
        ('Delivery', {
            'fields': ('estimated_delivery_date',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def has_add_permission(self, request):
        # Shipping methods are created automatically with orders
        return False
