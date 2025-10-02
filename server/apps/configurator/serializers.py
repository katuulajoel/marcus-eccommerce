from rest_framework import serializers
from .models import PriceAdjustmentRule, IncompatibilityRule

class PriceAdjustmentRuleSerializer(serializers.ModelSerializer):
    condition_option_name = serializers.CharField(source='condition_option.name', read_only=True)
    affected_option_name = serializers.CharField(source='affected_option.name', read_only=True)

    class Meta:
        model = PriceAdjustmentRule
        fields = '__all__'

class IncompatibilityRuleSerializer(serializers.ModelSerializer):
    option_a_name = serializers.CharField(source='option_a.name', read_only=True)
    option_b_name = serializers.CharField(source='option_b.name', read_only=True)

    class Meta:
        model = IncompatibilityRule
        fields = '__all__'
