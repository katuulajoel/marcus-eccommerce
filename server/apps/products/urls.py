from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, PartViewSet, PartOptionViewSet, StockViewSet

router = DefaultRouter()
router.register(r'', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]
