from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'exchange-rates', views.ExchangeRateViewSet, basename='exchange-rates')

urlpatterns = [
    path('', include(router.urls)),
    path('convert/', views.convert_currency, name='convert-currency'),
    path('info/<str:currency_code>/', views.get_currency_info, name='currency-info'),
    path('all/', views.get_all_currencies, name='all-currencies'),
]
