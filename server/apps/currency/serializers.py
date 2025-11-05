from rest_framework import serializers
from .models import ExchangeRate
from decimal import Decimal


class ExchangeRateSerializer(serializers.ModelSerializer):
    """Serializer for ExchangeRate model"""
    rate_from_ugx = serializers.SerializerMethodField()

    class Meta:
        model = ExchangeRate
        fields = [
            'id',
            'currency_code',
            'currency_name',
            'symbol',
            'decimal_places',
            'rate_to_ugx',
            'rate_from_ugx',
            'is_active',
            'rate_source',
            'last_updated',
        ]
        read_only_fields = ['id', 'last_updated']

    def get_rate_from_ugx(self, obj):
        """Calculate inverse rate (1 UGX = X currency)"""
        return float(obj.get_rate_from_ugx())


class CurrencyConversionSerializer(serializers.Serializer):
    """Serializer for currency conversion requests"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    from_currency = serializers.CharField(max_length=3, default='UGX')
    to_currency = serializers.CharField(max_length=3, required=True)

    def validate(self, data):
        """Validate currency codes"""
        from_currency = data.get('from_currency', 'UGX')
        to_currency = data['to_currency']

        # UGX is always valid (base currency)
        if from_currency != 'UGX':
            if not ExchangeRate.objects.filter(currency_code=from_currency, is_active=True).exists():
                raise serializers.ValidationError({
                    'from_currency': f'Currency {from_currency} is not available'
                })

        if to_currency != 'UGX':
            if not ExchangeRate.objects.filter(currency_code=to_currency, is_active=True).exists():
                raise serializers.ValidationError({
                    'to_currency': f'Currency {to_currency} is not available'
                })

        return data

    def convert(self):
        """Perform currency conversion"""
        validated_data = self.validated_data
        amount = validated_data['amount']
        from_currency = validated_data.get('from_currency', 'UGX')
        to_currency = validated_data['to_currency']

        converted_amount = ExchangeRate.convert(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency
        )

        return {
            'original_amount': float(amount),
            'from_currency': from_currency,
            'to_currency': to_currency,
            'converted_amount': float(converted_amount),
        }


class CurrencyInfoSerializer(serializers.Serializer):
    """Serializer for currency information response"""
    code = serializers.CharField()
    name = serializers.CharField()
    symbol = serializers.CharField()
    decimal_places = serializers.IntegerField()
    rate_to_ugx = serializers.FloatField()
    last_updated = serializers.CharField()
