from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Schema view configuration for Swagger UI
schema_view = get_schema_view(
    openapi.Info(
        title="Marcus E-commerce API",
        default_version='v1',
        description="API documentation for Marcus E-commerce backend",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    patterns=[
        # Make sure these patterns match your URL patterns exactly
        r'^api/products/.*',
        r'^api/orders/.*',
        r'^api/customers/.*',
        r'^api/configurator/.*',
        r'^api/preconfigured-products/.*',
    ],
)
