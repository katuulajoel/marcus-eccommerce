"""
Checkout API Views (Phase 4)
Separated for clarity - import these in urls.py
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from decimal import Decimal

from .services.checkout_service import get_checkout_service
from .services.shipping_service import get_shipping_service
from .services.payment_service import get_payment_service


@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_checkout(request):
    """
    Initiate checkout process

    Request body:
    {
        "session_id": "session-xxx"
    }

    Returns: Checkout session data
    """
    session_id = request.data.get('session_id')

    if not session_id:
        return Response({
            'error': 'session_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        checkout_service = get_checkout_service()
        checkout = checkout_service.create_checkout_session(session_id)

        return Response(checkout, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_checkout_session(request, session_id):
    """
    Get checkout session data

    Returns: Checkout session data or null if not found
    """
    try:
        checkout_service = get_checkout_service()
        checkout = checkout_service.get_checkout_session(session_id)

        if not checkout:
            return Response({
                'checkout': None
            }, status=status.HTTP_200_OK)

        return Response(checkout, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def save_shipping_address(request):
    """
    Save shipping address to checkout session

    Request body:
    {
        "session_id": "session-xxx",
        "recipient_name": "John Doe",
        "phone_number": "+256701234567",
        "address_line1": "Plot 123 Main St",
        "city": "Kampala",
        "country": "Uganda",
        "address_line2": ""  // optional
    }

    Returns: Updated checkout session with shipping options
    """
    session_id = request.data.get('session_id')

    if not session_id:
        return Response({
            'error': 'session_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        checkout_service = get_checkout_service()
        shipping_service = get_shipping_service()

        # Validate address
        address_data = {
            'recipient_name': request.data.get('recipient_name'),
            'phone_number': request.data.get('phone_number'),
            'address_line1': request.data.get('address_line1'),
            'city': request.data.get('city'),
            'country': request.data.get('country', 'Uganda'),
            'address_line2': request.data.get('address_line2', '')
        }

        is_valid, error = checkout_service.validate_address(address_data)
        if not is_valid:
            return Response({
                'error': error
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update checkout session
        checkout = checkout_service.update_checkout_session(session_id, {
            'shipping_address': address_data,
            'status': 'address_collected'
        })

        # Get shipping options
        cart_total = Decimal(checkout['cart_total'])
        city = address_data['city']

        shipping_methods = shipping_service.get_available_shipping_methods(
            cart_total=cart_total,
            city=city
        )

        return Response({
            'checkout': checkout,
            'shipping_options': shipping_methods
        }, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_shipping_options(request):
    """
    Get available shipping options

    Request body:
    {
        "session_id": "session-xxx"
    }

    Returns: List of shipping methods with costs
    """
    session_id = request.data.get('session_id')

    if not session_id:
        return Response({
            'error': 'session_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        checkout_service = get_checkout_service()
        shipping_service = get_shipping_service()

        checkout = checkout_service.get_checkout_session(session_id)
        if not checkout:
            return Response({
                'error': 'Checkout session not found'
            }, status=status.HTTP_404_NOT_FOUND)

        address = checkout.get('shipping_address', {})
        if not address.get('city'):
            return Response({
                'error': 'Shipping address not provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        cart_total = Decimal(checkout['cart_total'])
        city = address['city']

        shipping_methods = shipping_service.get_available_shipping_methods(
            cart_total=cart_total,
            city=city
        )

        return Response({
            'shipping_options': shipping_methods
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def select_shipping_method(request):
    """
    Select shipping method

    Request body:
    {
        "session_id": "session-xxx",
        "shipping_method": "standard"  // pickup, standard, or express
    }

    Returns: Updated checkout with order summary and payment methods
    """
    session_id = request.data.get('session_id')
    shipping_method = request.data.get('shipping_method')

    if not session_id or not shipping_method:
        return Response({
            'error': 'session_id and shipping_method are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        checkout_service = get_checkout_service()
        shipping_service = get_shipping_service()
        payment_service = get_payment_service()

        checkout = checkout_service.get_checkout_session(session_id)
        if not checkout:
            return Response({
                'error': 'Checkout session not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Validate shipping method
        address = checkout.get('shipping_address', {})
        city = address.get('city', '')

        is_valid, error = shipping_service.validate_shipping_method(shipping_method, city)
        if not is_valid:
            return Response({
                'error': error
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate shipping cost
        cart_total = Decimal(checkout['cart_total'])
        shipping_cost = shipping_service.calculate_shipping_cost(
            shipping_method, cart_total
        )

        # Update checkout session
        checkout = checkout_service.update_checkout_session(session_id, {
            'shipping_method': shipping_method,
            'shipping_cost': str(shipping_cost),
            'status': 'shipping_selected'
        })

        # Calculate order total
        order_total = cart_total + shipping_cost

        # Get payment methods
        payment_methods = payment_service.get_available_payment_methods(order_total)

        return Response({
            'checkout': checkout,
            'order_total': float(order_total),
            'payment_methods': payment_methods
        }, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_order_from_cart(request):
    """
    Create order from cart

    Request body:
    {
        "session_id": "session-xxx",
        "customer_name": "John Doe",
        "customer_phone": "+256701234567",
        "customer_email": "john@example.com"  // optional
    }

    Returns: Order details
    """
    session_id = request.data.get('session_id')
    customer_name = request.data.get('customer_name')
    customer_phone = request.data.get('customer_phone')
    customer_email = request.data.get('customer_email')

    if not all([session_id, customer_name, customer_phone]):
        return Response({
            'error': 'session_id, customer_name, and customer_phone are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        checkout_service = get_checkout_service()

        checkout = checkout_service.get_checkout_session(session_id)
        if not checkout:
            return Response({
                'error': 'Checkout session not found'
            }, status=status.HTTP_404_NOT_FOUND)

        if checkout['status'] != 'shipping_selected':
            return Response({
                'error': 'Please complete address and shipping selection first'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get or create customer
        customer = checkout_service.get_or_create_customer(
            name=customer_name,
            phone=customer_phone,
            email=customer_email
        )

        # Create shipping address
        address_data = checkout['shipping_address']
        shipping_address = checkout_service.save_shipping_address(address_data)

        # Calculate totals
        shipping_cost = Decimal(checkout['shipping_cost'])

        # Create order
        order = checkout_service.create_order_from_cart(
            session_id=session_id,
            customer=customer,
            shipping_address=shipping_address,
            shipping_cost=shipping_cost
        )

        # Get order summary
        order_summary = checkout_service.get_order_summary(order.id)

        return Response({
            'order': order_summary
        }, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_payment_link(request):
    """
    Generate payment link or USSD code

    Request body:
    {
        "session_id": "session-xxx",
        "payment_method": "stripe"  // stripe, mtn_mobile_money, airtel_money, cash_on_delivery
    }

    Returns: Payment link or USSD instructions
    """
    session_id = request.data.get('session_id')
    payment_method = request.data.get('payment_method')

    if not session_id or not payment_method:
        return Response({
            'error': 'session_id and payment_method are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        checkout_service = get_checkout_service()
        payment_service = get_payment_service()

        checkout = checkout_service.get_checkout_session(session_id)
        if not checkout:
            return Response({
                'error': 'Checkout session not found'
            }, status=status.HTTP_404_NOT_FOUND)

        order_id = checkout.get('order_id')
        if not order_id:
            return Response({
                'error': 'Order not created yet'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get order details
        order_summary = checkout_service.get_order_summary(order_id)
        order_total = Decimal(str(order_summary['total_price']))

        # Validate payment method
        is_valid, error = payment_service.validate_payment_method(
            payment_method, order_total
        )
        if not is_valid:
            return Response({
                'error': error
            }, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            'order_id': order_id,
            'payment_method': payment_method,
            'amount': float(order_total),
            'currency': order_summary['currency']
        }

        # Handle different payment methods
        if payment_method == 'stripe':
            try:
                payment_url = payment_service.create_stripe_checkout_session(order_id)
                response_data['payment_url'] = payment_url
                response_data['type'] = 'payment_link'
            except ValueError as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        elif payment_method in ['mtn_mobile_money', 'airtel_money']:
            phone = order_summary['customer_phone']
            instructions = payment_service.generate_mobile_money_instructions(
                provider=payment_method,
                order_id=order_id,
                phone_number=phone,
                amount=order_total
            )
            response_data['type'] = 'mobile_money'
            response_data['instructions'] = instructions

        elif payment_method == 'cash_on_delivery':
            response_data['type'] = 'cash_on_delivery'
            response_data['message'] = 'Order confirmed! Pay cash when you receive your delivery.'

        # Delete checkout session after payment generation
        checkout_service.delete_checkout_session(session_id)

        return Response(response_data, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
