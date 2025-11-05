from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.customers.models import Customer


class AIChatSession(models.Model):
    """
    Represents a conversation session with the AI assistant.
    Each user gets a unique session that persists across page loads.
    """
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Associated customer (null for anonymous users)"
    )
    context = models.JSONField(
        default=dict,
        help_text="Stores current page, cart state, configuration state, etc."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_chat_session'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Session {self.session_id} ({self.customer or 'Anonymous'})"


class AIChatMessage(models.Model):
    """
    Individual messages within a chat session.
    Stores both user queries and AI responses.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    session = models.ForeignKey(
        AIChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(
        default=dict,
        help_text="Product IDs, configuration suggestions, action types, etc."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_chat_message'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class AIEmbeddedDocument(models.Model):
    """
    Stores document embeddings for RAG (Retrieval Augmented Generation).
    Documents are chunks of product information, part descriptions, etc.
    """
    DOCUMENT_TYPE_CHOICES = [
        ('product', 'Preconfigured Product'),
        ('part_option', 'Part Option'),
        ('category', 'Category'),
        ('compatibility_rule', 'Compatibility Rule'),
        ('faq', 'FAQ'),
    ]

    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    document_id = models.IntegerField(help_text="ID of the source document")
    content = models.TextField(help_text="Text content to be embedded")

    # Vector embedding will be added after pgvector is set up
    # embedding = VectorField(dimensions=1536)  # For OpenAI embeddings

    metadata = models.JSONField(
        default=dict,
        help_text="Additional data like category_id, price, tags, etc."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_embedded_document'
        indexes = [
            models.Index(fields=['document_type', 'document_id']),
            models.Index(fields=['document_type']),
        ]
        # Vector index will be added via migration after pgvector setup

    def __str__(self):
        return f"{self.document_type}:{self.document_id} - {self.content[:50]}..."


class AIRecommendation(models.Model):
    """
    Tracks AI recommendations made to users for analytics.
    """
    session = models.ForeignKey(
        AIChatSession,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    recommended_product_ids = ArrayField(
        models.IntegerField(),
        default=list,
        help_text="List of recommended product IDs"
    )
    context = models.JSONField(
        default=dict,
        help_text="User query and context at time of recommendation"
    )
    user_action = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Action taken: viewed, added_to_cart, ignored"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_recommendation'
        ordering = ['-created_at']

    def __str__(self):
        return f"Recommendation for {self.session.session_id}"
