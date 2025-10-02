from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrdersViewSet, OrderProductViewSet, OrderItemViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'', OrdersViewSet)
router.register(r'products', OrderProductViewSet)
router.register(r'items', OrderItemViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
