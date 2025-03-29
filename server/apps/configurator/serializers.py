from rest_framework import serializers
from .models import PriceAdjustmentRule, IncompatibilityRule

class PriceAdjustmentRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceAdjustmentRule
        fields = '__all__'

class IncompatibilityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncompatibilityRule
        fields = '__all__'
