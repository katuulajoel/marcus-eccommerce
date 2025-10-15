from django.urls import path
from . import views

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
]
