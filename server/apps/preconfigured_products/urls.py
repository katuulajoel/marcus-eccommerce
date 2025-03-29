from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreConfiguredProductViewSet, PreConfiguredProductPartsViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register('products', PreConfiguredProductViewSet, basename='preconfigured-product')
router.register('parts', PreConfiguredProductPartsViewSet, basename='preconfigured-product-part')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
