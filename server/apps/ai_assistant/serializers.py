from rest_framework import serializers
from .models import AIChatSession, AIChatMessage, AIRecommendation


class AIChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatMessage
        fields = ['id', 'role', 'content', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']


class AIChatSessionSerializer(serializers.ModelSerializer):
    messages = AIChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AIChatSession
        fields = ['id', 'session_id', 'customer', 'context', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatRequestSerializer(serializers.Serializer):
    """
    Serializer for incoming chat messages from the frontend.
    """
    session_id = serializers.CharField(max_length=255)
    message = serializers.CharField()
    context = serializers.JSONField(required=False, default=dict)


class ChatResponseSerializer(serializers.Serializer):
    """
    Serializer for AI responses back to the frontend.
    """
    message_id = serializers.IntegerField()
    role = serializers.CharField()
    content = serializers.CharField()
    metadata = serializers.JSONField()
    timestamp = serializers.DateTimeField()


class AIRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRecommendation
        fields = ['id', 'session', 'recommended_product_ids', 'context', 'user_action', 'created_at']
        read_only_fields = ['id', 'created_at']
