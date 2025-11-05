from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, PartViewSet, PartOptionViewSet, StockViewSet
from .currency_views import currency_config

router = DefaultRouter()
router.register(r'', CategoryViewSet, basename='category')

urlpatterns = [
    path('currency-config/', currency_config, name='currency-config'),
    path('', include(router.urls)),
]
