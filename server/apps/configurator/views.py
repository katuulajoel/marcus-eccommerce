from rest_framework.viewsets import ModelViewSet
from .models import PriceAdjustmentRule, IncompatibilityRule
from .serializers import PriceAdjustmentRuleSerializer, IncompatibilityRuleSerializer
from .permissions import AllowGetAnonymously

class PriceAdjustmentRuleViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing price adjustment rules.
    
    **Authentication required**: 
    - GET: No (anyone can view rules)
    - POST, PUT, PATCH, DELETE: Yes (only authenticated users)
    
    Regular users can only view rules.
    Staff users have full CRUD access.
    """
    queryset = PriceAdjustmentRule.objects.all()
    serializer_class = PriceAdjustmentRuleSerializer
    permission_classes = [AllowGetAnonymously]
    
    def get_queryset(self):
        """
        Return all price adjustment rules.
        """
        return PriceAdjustmentRule.objects.all()

class IncompatibilityRuleViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing incompatibility rules.
    
    **Authentication required**: 
    - GET: No (anyone can view rules)
    - POST, PUT, PATCH, DELETE: Yes (only authenticated users)
    
    Regular users can only view rules.
    Staff users have full CRUD access.
    """
    queryset = IncompatibilityRule.objects.all()
    serializer_class = IncompatibilityRuleSerializer
    permission_classes = [AllowGetAnonymously]
    
    def get_queryset(self):
        """
        Return all incompatibility rules.
        """
        return IncompatibilityRule.objects.all()
