from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderProductViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'order-products', OrderProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
