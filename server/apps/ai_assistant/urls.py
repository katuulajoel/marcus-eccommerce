from django.urls import path
from . import views
from . import views_checkout

app_name = 'ai_assistant'

urlpatterns = [
    # Main chat endpoint
    path('chat/', views.chat, name='chat'),

    # Session management
    path('session/<str:session_id>/', views.get_session, name='get_session'),
    path('session/<str:session_id>/clear/', views.clear_session, name='clear_session'),

    # Additional AI features
    path('recommend/', views.recommend_products, name='recommend_products'),
    path('validate-config/', views.validate_configuration, name='validate_configuration'),

    # Cart management (Redis-based - Phase 3)
    # IMPORTANT: Specific paths must come before dynamic paths!
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/<str:session_id>/', views.get_cart, name='get_cart'),  # Must be last!

    # Checkout endpoints (Phase 4)
    path('checkout/initiate/', views_checkout.initiate_checkout, name='initiate_checkout'),
    path('checkout/<str:session_id>/', views_checkout.get_checkout_session, name='get_checkout_session'),
    path('checkout/address/', views_checkout.save_shipping_address, name='save_shipping_address'),
    path('checkout/shipping-options/', views_checkout.get_shipping_options, name='get_shipping_options'),
    path('checkout/select-shipping/', views_checkout.select_shipping_method, name='select_shipping_method'),
    path('checkout/create-order/', views_checkout.create_order_from_cart, name='create_order_from_cart'),
    path('checkout/payment-link/', views_checkout.generate_payment_link, name='generate_payment_link'),
]
