from rest_framework.viewsets import ModelViewSet
from .models import PriceAdjustmentRule, IncompatibilityRule
from .serializers import PriceAdjustmentRuleSerializer, IncompatibilityRuleSerializer

class PriceAdjustmentRuleViewSet(ModelViewSet):
    queryset = PriceAdjustmentRule.objects.all()
    serializer_class = PriceAdjustmentRuleSerializer

class IncompatibilityRuleViewSet(ModelViewSet):
    queryset = IncompatibilityRule.objects.all()
    serializer_class = IncompatibilityRuleSerializer
