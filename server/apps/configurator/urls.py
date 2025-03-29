from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PriceAdjustmentRuleViewSet, IncompatibilityRuleViewSet

router = DefaultRouter()
router.register(r'price-adjustments', PriceAdjustmentRuleViewSet)
router.register(r'incompatibilities', IncompatibilityRuleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
