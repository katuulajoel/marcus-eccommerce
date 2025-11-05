from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal
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
from .services.cart_service import get_cart_service
from .services.checkout_service import get_checkout_service
from .services.shipping_service import get_shipping_service
from .services.payment_service import get_payment_service
from .orchestration.langgraph_workflow import get_multi_agent_workflow
from .orchestration.state_manager import get_state_manager
from .adapters.channel_adapter import get_channel_adapter


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
    # Gracefully handle OpenAI quota errors - RAG is optional for checkout flow
    rag_context = {}
    try:
        rag_service = get_rag_service()
        rag_context = rag_service.retrieve_context_for_query(user_message, context)
    except Exception as e:
        # Log but don't fail - agent can work without RAG for checkout
        print(f"⚠️ RAG unavailable (likely OpenAI quota): {str(e)[:100]}")

    # Get conversation history for context (last 10 messages)
    # Now include metadata for better context preservation
    all_messages = session.messages.order_by('created_at').values('role', 'content', 'metadata')
    message_count = all_messages.count()

    if message_count > 10:
        conversation_history = list(all_messages[message_count - 10:])
    else:
        conversation_history = list(all_messages)

    # Get channel from context (default to web)
    channel = context.get('channel', 'web')

    # Generate AI response using MULTI-AGENT WORKFLOW (NEW!)
    workflow = get_multi_agent_workflow()
    ai_response = workflow.run(
        session_id=session_id,
        user_message=user_message,
        conversation_history=conversation_history,
        user_context={
            **enriched_context,
            **rag_context,
        }
    )

    # Format response for channel
    channel_adapter = get_channel_adapter(channel)
    ai_response = channel_adapter.format_response(ai_response)

    # Enhance metadata with product recommendations ONLY if intent indicates they're relevant
    enhanced_metadata = ai_response['metadata'].copy()
    intent = rag_context.get('intent', 'general')

    # Only include products if the intent requires recommendations
    if rag_context.get('products'):
        enhanced_metadata['products'] = rag_context['products'][:3]  # Top 3 products
        enhanced_metadata['intent'] = intent

    # Check if AI used cart tools and add action metadata
    tools_used = enhanced_metadata.get('tools_used', [])
    workflow_info = enhanced_metadata.get('workflow', {})

    # Add workflow information to metadata
    if workflow_info:
        enhanced_metadata['agent_used'] = workflow_info.get('final_agent')
        enhanced_metadata['agent_iterations'] = workflow_info.get('iterations')

    if 'add_to_cart' in tools_used or 'view_cart' in tools_used:
        # Fetch current cart state
        cart_service = get_cart_service()
        cart = cart_service.get_cart(session_id)

        # Update state manager with cart count
        state_manager = get_state_manager(session_id)
        state_manager.set_cart_items_count(cart.get('item_count', 0))

        action_type = 'item_added' if 'add_to_cart' in tools_used else 'cart_updated'

        enhanced_metadata['action'] = {
            'type': action_type,
            'cart_items': cart.get('items', []),
            'cart_total': cart.get('subtotal', 0),
            'item_count': cart.get('item_count', 0)
        }

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


# ============================================================================
# CART MANAGEMENT ENDPOINTS - Redis-based Shopping Cart
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def add_to_cart(request):
    """
    Add item to shopping cart.

    Request body:
    {
        "session_id": "session-xxx" or "wa_256701618576",
        "product_id": 123,
        "name": "Product Name",
        "price": 120000,
        "quantity": 2,
        "configuration": {...},  // optional
        "image_url": "https://...",  // optional
        "category_id": 1  // optional
    }

    Returns: Updated cart
    """
    session_id = request.data.get('session_id')
    product_id = request.data.get('product_id')
    name = request.data.get('name')
    price = request.data.get('price')
    quantity = request.data.get('quantity', 1)
    configuration = request.data.get('configuration')
    image_url = request.data.get('image_url')
    category_id = request.data.get('category_id')
    config_details = request.data.get('config_details')

    # Validation
    if not all([session_id, product_id, name, price]):
        return Response({
            'error': 'session_id, product_id, name, and price are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        cart_service = get_cart_service()
        cart_service.add_item(
            session_id=session_id,
            product_id=product_id,
            name=name,
            price=Decimal(str(price)),
            quantity=quantity,
            configuration=configuration,
            image_url=image_url,
            category_id=category_id,
            config_details=config_details
        )

        # Return updated cart
        cart = cart_service.get_cart(session_id)
        return Response(cart, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart(request, session_id):
    """
    Get cart contents for a session.

    GET /api/ai-assistant/cart/{session_id}/

    Returns: Cart with items, subtotal, item_count
    """
    try:
        cart_service = get_cart_service()
        cart = cart_service.get_cart(session_id)
        return Response(cart, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def remove_from_cart(request):
    """
    Remove item from cart.

    Request body:
    {
        "session_id": "session-xxx",
        "item_id": "123_hash"
    }

    Returns: Updated cart
    """
    session_id = request.data.get('session_id')
    item_id = request.data.get('item_id')

    if not all([session_id, item_id]):
        return Response({
            'error': 'session_id and item_id are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        cart_service = get_cart_service()
        cart_service.remove_item(session_id, item_id)

        # Return updated cart
        cart = cart_service.get_cart(session_id)
        return Response(cart, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_cart_quantity(request):
    """
    Update item quantity in cart.

    Request body:
    {
        "session_id": "session-xxx",
        "item_id": "123_hash",
        "quantity": 3
    }

    Returns: Updated cart
    """
    session_id = request.data.get('session_id')
    item_id = request.data.get('item_id')
    quantity = request.data.get('quantity')

    if not all([session_id, item_id]) or quantity is None:
        return Response({
            'error': 'session_id, item_id, and quantity are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        cart_service = get_cart_service()
        cart_service.update_quantity(session_id, item_id, int(quantity))

        # Return updated cart
        cart = cart_service.get_cart(session_id)
        return Response(cart, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def clear_cart(request):
    """
    Clear all items from cart.

    Request body:
    {
        "session_id": "session-xxx"
    }

    Returns: Success message
    """
    session_id = request.data.get('session_id')

    if not session_id:
        return Response({
            'error': 'session_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        cart_service = get_cart_service()
        cart_service.clear_cart(session_id)

        return Response({
            'message': 'Cart cleared successfully'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
