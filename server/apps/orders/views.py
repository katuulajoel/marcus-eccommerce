from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Orders, OrderProduct, OrderItem, Payment
from .serializers import OrdersSerializer, OrderProductSerializer, OrderItemSerializer, PaymentSerializer
from .permissions import AllowPostAnonymously

class OrdersViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing orders.
    
    **Authentication required**: 
    - POST: No (anyone can create orders)
    - GET, PUT, PATCH, DELETE: Yes (only authenticated users)
    
    Regular users can only see their own orders.
    Staff users can see all orders.
    """
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [AllowPostAnonymously]
    
    def get_queryset(self):
        """
        Filter orders to return only orders belonging to the current user
        if the user is not a staff member
        """
        queryset = Orders.objects.all()
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            # If a regular user is logged in, only show their orders
            queryset = queryset.filter(customer__user=self.request.user)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def record_payment(self, request, pk=None):
        """
        Record a payment for an order

        Required fields:
        - amount: Decimal
        - payment_method: String
        - paid_by: String ('customer' or 'delivery_person')
        - transaction_reference: String (optional)
        """
        order = self.get_object()

        # Validate amount
        amount = request.data.get('amount')
        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from decimal import Decimal
            amount = Decimal(str(amount))
            if amount <= 0:
                return Response(
                    {'error': 'Amount must be greater than 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if payment would exceed total price
        if order.amount_paid + amount > order.total_price:
            return Response(
                {'error': f'Payment amount exceeds remaining balance of {order.balance_due}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create payment
        payment_data = {
            'order': order.id,
            'amount': amount,
            'payment_method': request.data.get('payment_method', 'Unknown'),
            'paid_by': request.data.get('paid_by', 'customer'),
            'transaction_reference': request.data.get('transaction_reference', ''),
        }

        serializer = PaymentSerializer(data=payment_data)
        if serializer.is_valid():
            serializer.save()

            # Refresh order data to get updated payment status
            order.refresh_from_db()
            order_serializer = OrdersSerializer(order)

            return Response({
                'message': 'Payment recorded successfully',
                'payment': serializer.data,
                'order': order_serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderProductViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing order products.
    
    **Authentication required**: Yes
    
    Only authenticated users can access this endpoint.
    Regular users can only see their own order products.
    Staff users can see all order products.
    """
    queryset = OrderProduct.objects.all()
    serializer_class = OrderProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter order products to return only those belonging to the current user's orders
        if the user is not a staff member
        """
        queryset = OrderProduct.objects.all()
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            # If a regular user is logged in, only show their order products
            queryset = queryset.filter(order__customer__user=self.request.user)
        return queryset

class OrderItemViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing order items.

    **Authentication required**: Yes

    Only authenticated users can access this endpoint.
    Regular users can only see their own order items.
    Staff users can see all order items.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter order items to return only those belonging to the current user's orders
        if the user is not a staff member
        """
        queryset = OrderItem.objects.all()
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            # If a regular user is logged in, only show their order items
            queryset = queryset.filter(order_product__order__customer__user=self.request.user)
        return queryset


class PaymentViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing payments.

    **Authentication required**: Yes

    Only authenticated users can access this endpoint.
    Regular users can only see their own payments.
    Staff users can see all payments.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter payments to return only those belonging to the current user's orders
        if the user is not a staff member
        """
        queryset = Payment.objects.all()
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            # If a regular user is logged in, only show their payments
            queryset = queryset.filter(order__customer__user=self.request.user)
        return queryset
