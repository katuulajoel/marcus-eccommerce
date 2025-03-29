from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrdersViewSet, OrderProductViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'orders', OrdersViewSet)
router.register(r'order-products', OrderProductViewSet)
router.register(r'order-items', OrderItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
