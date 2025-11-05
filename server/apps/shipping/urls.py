from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShippingConstantsViewSet, ShippingZoneViewSet, ShippingRateViewSet,
    ShippingCalculatorViewSet, OrderShippingMethodViewSet
)

router = DefaultRouter()
router.register(r'constants', ShippingConstantsViewSet, basename='shipping-constants')
router.register(r'zones', ShippingZoneViewSet, basename='shipping-zones')
router.register(r'rates', ShippingRateViewSet, basename='shipping-rates')
router.register(r'calculator', ShippingCalculatorViewSet, basename='shipping-calculator')
router.register(r'order-shipping', OrderShippingMethodViewSet, basename='order-shipping')

urlpatterns = [
    path('', include(router.urls)),
]
