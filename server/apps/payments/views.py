from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import PaymentGatewayConfig, PaymentTransaction
from .serializers import (
    PaymentGatewayConfigSerializer,
    PaymentTransactionSerializer,
    InitiatePaymentSerializer,
    VerifyPaymentSerializer
)
from .services import PaymentService
from apps.orders.models import Orders


class PaymentGatewayViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing available payment gateways

    Only active gateways are shown
    """
    queryset = PaymentGatewayConfig.objects.filter(is_active=True)
    serializer_class = PaymentGatewayConfigSerializer
    permission_classes = [AllowAny]


class PaymentTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing payment transactions

    Users can only view their own transactions
    """
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter transactions to show only user's transactions"""
        if self.request.user.is_staff:
            return PaymentTransaction.objects.all()
        return PaymentTransaction.objects.filter(order__customer__user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    Initiate a payment transaction

    Required fields:
    - order_id: Order ID
    - gateway: Payment gateway (stripe, mtn_momo, airtel_money)
    - amount: Payment amount
    - currency: Currency code (default: USD)

    Optional fields:
    - customer_phone: Override customer phone
    - customer_email: Override customer email
    """
    serializer = InitiatePaymentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        # Verify user owns the order
        order = Orders.objects.get(id=data['order_id'])
        if not request.user.is_staff and order.customer.user != request.user:
            return Response(
                {'error': 'You do not have permission to pay for this order'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Prepare customer data
        customer_data = {
            'email': data.get('customer_email') or order.customer.email,
            'phone': data.get('customer_phone') or order.customer.phone,
            'name': order.customer.name
        }

        # Initiate payment
        transaction, result = PaymentService.initiate_payment(
            order_id=data['order_id'],
            gateway_name=data['gateway'],
            amount=data['amount'],
            currency=data['currency'],
            customer_data=customer_data
        )

        # Return transaction data with action details from initialization
        response_data = PaymentTransactionSerializer(transaction).data
        response_data['action_required'] = result.requires_action
        response_data['action_data'] = result.action_data
        response_data['message'] = result.message

        return Response(response_data, status=status.HTTP_201_CREATED)

    except Orders.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Payment initiation failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """
    Verify payment transaction status

    Required fields:
    - transaction_id: PaymentTransaction ID
    """
    serializer = VerifyPaymentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    transaction_id = serializer.validated_data['transaction_id']

    try:
        # Verify user owns the transaction
        transaction = PaymentTransaction.objects.get(id=transaction_id)
        if not request.user.is_staff and transaction.order.customer.user != request.user:
            return Response(
                {'error': 'You do not have permission to view this transaction'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verify payment
        result = PaymentService.verify_payment(transaction_id)

        # Refresh transaction from DB
        transaction.refresh_from_db()

        response_data = PaymentTransactionSerializer(transaction).data
        response_data['verification_result'] = {
            'success': result.success,
            'status': result.status,
            'message': result.message,
            'error': result.error
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except PaymentTransaction.DoesNotExist:
        return Response(
            {'error': 'Transaction not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Payment verification failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook endpoint

    Stripe sends events to this endpoint
    """
    payload = request.body
    signature = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        import json
        payload_dict = json.loads(payload)

        result = PaymentService.process_webhook(
            gateway_name='stripe',
            payload=payload_dict,
            signature=signature
        )

        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def mtn_momo_webhook(request):
    """
    MTN MoMo callback endpoint
    """
    try:
        result = PaymentService.process_webhook(
            gateway_name='mtn_momo',
            payload=request.data
        )

        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def airtel_webhook(request):
    """
    Airtel Money callback endpoint
    """
    try:
        result = PaymentService.process_webhook(
            gateway_name='airtel_money',
            payload=request.data
        )

        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
