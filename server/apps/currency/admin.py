from django.contrib import admin
from .models import ExchangeRate


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    """Admin interface for managing exchange rates"""
    list_display = [
        'currency_code',
        'currency_name',
        'symbol',
        'rate_to_ugx',
        'rate_from_ugx_display',
        'is_active',
        'rate_source',
        'last_updated',
    ]
    list_filter = ['is_active', 'rate_source', 'last_updated']
    search_fields = ['currency_code', 'currency_name']
    readonly_fields = ['last_updated', 'created_at', 'rate_from_ugx_display']

    fieldsets = (
        ('Currency Information', {
            'fields': ('currency_code', 'currency_name', 'symbol', 'decimal_places')
        }),
        ('Exchange Rate', {
            'fields': ('rate_to_ugx', 'rate_from_ugx_display', 'rate_source'),
            'description': 'Exchange rate: 1 [Currency] = X UGX'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def rate_from_ugx_display(self, obj):
        """Display inverse rate for convenience"""
        return f"1 UGX = {obj.get_rate_from_ugx():.6f} {obj.currency_code}"
    rate_from_ugx_display.short_description = 'Rate from UGX'

    def save_model(self, request, obj, form, change):
        """Ensure rate source is set when manually saving"""
        if not change or 'rate_to_ugx' in form.changed_data:
            # If creating new or updating rate manually
            obj.rate_source = 'manual'
        super().save_model(request, obj, form, change)

    class Meta:
        verbose_name = 'Exchange Rate'
        verbose_name_plural = 'Exchange Rates'
