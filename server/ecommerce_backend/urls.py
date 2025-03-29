# Django URL configuration

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/', include('server.apps.products.urls')),
    path('api/orders/', include('server.apps.orders.urls')),
    path('api/customers/', include('server.apps.customers.urls')),
    path('api/configurator/', include('server.apps.configurator.urls')),
]