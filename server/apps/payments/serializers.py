from rest_framework import serializers
from .models import PaymentGatewayConfig, PaymentTransaction
from apps.orders.serializers import PaymentSerializer as OrderPaymentSerializer


class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewayConfig
        fields = ('id', 'gateway_name', 'is_active', 'environment')


class PaymentTransactionSerializer(serializers.ModelSerializer):
    payment_details = OrderPaymentSerializer(source='payment', read_only=True)
    gateway_display = serializers.CharField(source='get_gateway_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = (
            'id', 'order', 'gateway', 'gateway_display', 'amount', 'currency',
            'status', 'status_display', 'gateway_transaction_id', 'gateway_reference',
            'customer_phone', 'customer_email', 'error_message',
            'created_at', 'updated_at', 'completed_at', 'payment_details'
        )
        read_only_fields = (
            'id', 'gateway_transaction_id', 'gateway_response', 'error_message',
            'created_at', 'updated_at', 'completed_at'
        )


class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    gateway = serializers.ChoiceField(
        choices=['stripe', 'mtn_momo', 'airtel_money'],
        required=True
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=3, default='USD')
    customer_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    customer_email = serializers.EmailField(required=False, allow_blank=True)


class VerifyPaymentSerializer(serializers.Serializer):
    transaction_id = serializers.IntegerField(required=True)
