from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'gateways', views.PaymentGatewayViewSet, basename='payment-gateway')
router.register(r'transactions', views.PaymentTransactionViewSet, basename='payment-transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('initiate/', views.initiate_payment, name='initiate_payment'),
    path('verify/', views.verify_payment, name='verify_payment'),

    # Webhooks
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhooks/mtn-momo/', views.mtn_momo_webhook, name='mtn_momo_webhook'),
    path('webhooks/airtel/', views.airtel_webhook, name='airtel_webhook'),
]
