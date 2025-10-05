# Django URL configuration

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .swagger_permissions import SwaggerPermission
from .swagger import schema_view
from django.conf import settings
from django.conf.urls.static import static

# Import viewsets for top-level routes
from rest_framework.routers import DefaultRouter
from apps.products.views import PartViewSet, PartOptionViewSet, StockViewSet

# Create router for top-level product-related resources
products_router = DefaultRouter()
products_router.register(r'parts', PartViewSet, basename='part')
products_router.register(r'part-options', PartOptionViewSet, basename='part-option')
products_router.register(r'stock', StockViewSet, basename='stock')

# Define all API URL patterns
api_patterns = [
    path('categories/', include('apps.products.urls')),
    path('orders/', include('apps.orders.urls')),
    path('customers/', include('apps.customers.urls')),
    path('configurator/', include('apps.configurator.urls')),
    path('preconfigured-products/', include('apps.preconfigured_products.urls')),
    path('auth/', include('apps.authentication.urls')),
    path('payments/', include('apps.payments.urls')),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Built-in Django REST framework auth views for login/logout
    path('drf-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Top-level product resources
    path('', include(products_router.urls)),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include all API endpoints under the 'api/' prefix
    path('api/', include(api_patterns)),
    
    # API Root redirects to Swagger UI
    path('', RedirectView.as_view(url='/api/swagger/', permanent=False)),
    
    # Swagger documentation
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Add static and media URLs for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)