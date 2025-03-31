from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, PartViewSet, PartOptionViewSet, StockViewSet

router = DefaultRouter()
router.register(r'', CategoryViewSet)
router.register(r'parts', PartViewSet)
router.register(r'part-options', PartOptionViewSet)
router.register(r'stock', StockViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
