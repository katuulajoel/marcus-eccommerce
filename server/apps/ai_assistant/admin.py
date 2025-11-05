from django.contrib import admin
from .models import AIChatSession, AIChatMessage, AIEmbeddedDocument, AIRecommendation


class AIChatMessageInline(admin.TabularInline):
    model = AIChatMessage
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('role', 'content', 'metadata', 'created_at')


@admin.register(AIChatSession)
class AIChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'customer', 'created_at', 'updated_at', 'message_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('session_id', 'customer__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AIChatMessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


@admin.register(AIChatMessage)
class AIChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'content_preview', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'session__session_id')
    readonly_fields = ('created_at',)

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(AIEmbeddedDocument)
class AIEmbeddedDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_type', 'document_id', 'content_preview', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('content', 'document_id')
    readonly_fields = ('created_at', 'updated_at')

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'product_ids_preview', 'user_action', 'created_at')
    list_filter = ('user_action', 'created_at')
    search_fields = ('session__session_id',)
    readonly_fields = ('created_at',)

    def product_ids_preview(self, obj):
        ids = obj.recommended_product_ids[:5]
        preview = ', '.join(map(str, ids))
        if len(obj.recommended_product_ids) > 5:
            preview += '...'
        return preview
    product_ids_preview.short_description = 'Recommended Products'
