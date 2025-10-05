from django.contrib import admin
from .models import PaymentGatewayConfig, PaymentTransaction


@admin.register(PaymentGatewayConfig)
class PaymentGatewayConfigAdmin(admin.ModelAdmin):
    list_display = ('gateway_name', 'is_active', 'environment', 'created_at')
    list_filter = ('gateway_name', 'is_active', 'environment')
    search_fields = ('gateway_name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'gateway', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('gateway', 'status', 'currency')
    search_fields = ('gateway_transaction_id', 'customer_email', 'customer_phone')
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'gateway_response')
    raw_id_fields = ('order', 'payment')
