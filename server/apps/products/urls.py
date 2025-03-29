from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, PartViewSet, PartOptionViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'parts', PartViewSet)
router.register(r'options', PartOptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
