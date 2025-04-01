from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PreConfiguredProductViewSet, 
    PreConfiguredProductPartsViewSet,
    BestSellingProductView,
    TopProductsPerCategoryViewSet
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register('products', PreConfiguredProductViewSet, basename='preconfigured-product')
router.register('parts', PreConfiguredProductPartsViewSet, basename='preconfigured-product-part')

# The API URLs are determined automatically by the router, plus our custom API views
urlpatterns = [
    path('', include(router.urls)),
    path('best-selling/', BestSellingProductView.as_view(), name='best-selling-product'),
    path('top-products/', TopProductsPerCategoryViewSet.as_view({'get': 'list'}), name='top-products'),
]
