# Django URL configuration

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/configurator/', include('apps.configurator.urls')),
]