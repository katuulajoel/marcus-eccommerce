from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrdersViewSet, OrderProductViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'', OrdersViewSet)
router.register(r'products', OrderProductViewSet)
router.register(r'items', OrderItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
