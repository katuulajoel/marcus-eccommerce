from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import AIChatSession, AIChatMessage, AIRecommendation
from .serializers import (
    AIChatSessionSerializer,
    AIChatMessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer
)
from .services.agent_service import get_agent_service
from .services.context_builder import context_builder
from .services.rag_service_new import get_rag_service


@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    """
    Main chat endpoint. Receives a user message and returns an AI response.

    Request body:
    {
        "session_id": "session-xxx",
        "message": "I need a mountain bike",
        "context": {
            "currentPage": "/customize",
            "categoryId": 1,
            "configuration": {...}
        }
    }
    """
    serializer = ChatRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    session_id = serializer.validated_data['session_id']
    user_message = serializer.validated_data['message']
    context = serializer.validated_data.get('context', {})

    # Get or create session
    session, created = AIChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={
            'context': context,
            'customer': request.user if request.user.is_authenticated else None
        }
    )

    # Update session context if provided
    if context and not created:
        session.context = context
        session.save()

    # Save user message
    user_msg = AIChatMessage.objects.create(
        session=session,
        role='user',
        content=user_message,
        metadata={}
    )

    # Build enriched context with database information
    enriched_context = context_builder.build_enriched_context(context)

    # Retrieve relevant information using RAG (LlamaIndex-based)
    rag_service = get_rag_service()
    rag_context = rag_service.retrieve_context_for_query(user_message, context)

    # Get conversation history for context (last 10 messages)
    all_messages = session.messages.order_by('created_at').values('role', 'content')
    message_count = all_messages.count()

    if message_count > 10:
        conversation_history = list(all_messages[message_count - 10:])
    else:
        conversation_history = list(all_messages)

    # Generate AI response using LangChain Agent service
    agent_service = get_agent_service()
    ai_response = agent_service.generate_response(
        user_message=user_message,
        context={**enriched_context, **rag_context},
        conversation_history=conversation_history
    )

    # Enhance metadata with product recommendations ONLY if intent indicates they're relevant
    enhanced_metadata = ai_response['metadata'].copy()
    intent = rag_context.get('intent', 'general')

    # Only include products if the intent requires recommendations
    if rag_context.get('products'):
        enhanced_metadata['products'] = rag_context['products'][:3]  # Top 3 products
        enhanced_metadata['intent'] = intent

    # Save AI response
    ai_msg = AIChatMessage.objects.create(
        session=session,
        role='assistant',
        content=ai_response['content'],
        metadata=enhanced_metadata
    )

    # Track recommendations ONLY if products were actually included in the response
    if enhanced_metadata.get('products'):
        product_ids = [p['id'] for p in enhanced_metadata['products']]
        AIRecommendation.objects.create(
            session=session,
            recommended_product_ids=product_ids,
            context={'query': user_message, 'intent': intent}
        )

    # Return response
    response_data = {
        'message_id': ai_msg.id,
        'role': ai_msg.role,
        'content': ai_msg.content,
        'metadata': enhanced_metadata,
        'timestamp': ai_msg.created_at
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_session(request, session_id):
    """
    Retrieve a chat session with all its messages.
    """
    session = get_object_or_404(AIChatSession, session_id=session_id)
    serializer = AIChatSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def clear_session(request, session_id):
    """
    Clear all messages in a session (keeps the session itself).
    """
    session = get_object_or_404(AIChatSession, session_id=session_id)
    session.messages.all().delete()
    return Response({'message': 'Session cleared successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def recommend_products(request):
    """
    Get product recommendations based on user query.

    Request body:
    {
        "query": "I need a bike for trail riding",
        "category_id": 1,
        "price_max": 2000
    }
    """
    query = request.data.get('query', '')
    category_id = request.data.get('category_id')
    price_max = request.data.get('price_max')

    if not query:
        return Response({
            'error': 'Query is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Search for matching products using RAG service
    rag_service = get_rag_service()
    products = rag_service.search_products(query, category_id, price_max)

    return Response({
        'recommended_products': products,
        'explanation': f"Found {len(products)} products matching your criteria"
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_configuration(request):
    """
    Validate a product configuration and provide AI suggestions.

    Request body:
    {
        "category_id": 1,
        "configuration": {
            "Frame": "123",
            "Wheels": "456"
        }
    }
    """
    category_id = request.data.get('category_id')
    configuration = request.data.get('configuration', {})

    if not category_id or not configuration:
        return Response({
            'error': 'category_id and configuration are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate configuration using context builder
    validation_result = context_builder.validate_configuration(
        category_id,
        configuration
    )

    return Response(validation_result, status=status.HTTP_200_OK)
