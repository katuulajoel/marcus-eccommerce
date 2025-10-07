from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from .models import Orders, OrderProduct, OrderItem, Payment, ShippingAddress
from .serializers import OrdersSerializer, OrderProductSerializer, OrderItemSerializer, PaymentSerializer
from .permissions import AllowPostAnonymously
from apps.customers.models import Customer
from apps.products.models import PartOption, Category
from apps.shipping.models import ShippingZone, ShippingRate, OrderShippingMethod
from apps.shipping.services import get_shipping_options

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

    def create(self, request, *args, **kwargs):
        """
        Create a new order with products, shipping address, and shipping method.

        Expected request data:
        {
            "shipping_address": {...},
            "shipping_zone_id": 1,
            "shipping_rate_id": 2,  // Optional - will recalculate if not provided
            "products": [
                {
                    "name": "Product Name",
                    "category_id": 1,
                    "price": 450,
                    "quantity": 1,
                    "configuration": {
                        "frame": {"name": "Full-Suspension Frame", "price": 130},
                        ...
                    }
                }
            ]
        }
        """
        # Get the authenticated user's customer record
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to create an order'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'Customer profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract data from request
        shipping_address_data = request.data.get('shipping_address')
        products_data = request.data.get('products', [])
        shipping_zone_id = request.data.get('shipping_zone_id')
        shipping_rate_id = request.data.get('shipping_rate_id')

        if not products_data:
            return Response(
                {'error': 'At least one product is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not shipping_zone_id:
            return Response(
                {'error': 'Shipping zone is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate shipping zone
        try:
            shipping_zone = ShippingZone.objects.get(id=shipping_zone_id, is_active=True)
        except ShippingZone.DoesNotExist:
            return Response(
                {'error': 'Invalid or inactive shipping zone'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create shipping address
        shipping_address = None
        if shipping_address_data:
            shipping_address = ShippingAddress.objects.create(**shipping_address_data)

        # Calculate products subtotal and build cart items for shipping calculation
        subtotal = Decimal('0.00')
        cart_items = []

        for product in products_data:
            price = Decimal(str(product.get('price', 0)))
            quantity = int(product.get('quantity', 1))
            subtotal += price * quantity

            # Build cart item for shipping calculation
            category_id = product.get('category_id')
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    cart_items.append({
                        'category': category,
                        'quantity': quantity
                    })
                except Category.DoesNotExist:
                    pass

        # Calculate shipping options
        shipping_cost = Decimal('0.00')
        shipping_details = None

        if cart_items:
            try:
                shipping_options = get_shipping_options(cart_items, shipping_zone)

                if not shipping_options:
                    return Response(
                        {'error': 'No shipping options available for this zone and cart'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Find the selected rate or use first option
                if shipping_rate_id:
                    selected_option = next(
                        (opt for opt in shipping_options if opt['rate_id'] == shipping_rate_id),
                        None
                    )
                    if not selected_option:
                        return Response(
                            {'error': 'Invalid shipping rate selected'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    # Default to first (usually cheapest/standard) option
                    selected_option = shipping_options[0]

                shipping_cost = Decimal(str(selected_option['total_cost_ugx']))
                shipping_details = selected_option

            except Exception as e:
                return Response(
                    {'error': f'Shipping calculation failed: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Calculate total price (subtotal + shipping)
        total_price = subtotal + shipping_cost

        # Create order
        order = Orders.objects.create(
            customer=customer,
            shipping_address=shipping_address,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total_price=total_price
        )

        # Create shipping method record
        if shipping_details:
            estimated_delivery_date = None
            if 'estimated_delivery_date' in shipping_details:
                estimated_delivery_date = shipping_details['estimated_delivery_date']

            OrderShippingMethod.objects.create(
                order=order,
                zone=shipping_zone,
                rate_id=shipping_details.get('rate_id'),
                delivery_method=shipping_details['delivery_method'],
                service_level=shipping_details['service_level'],
                base_shipping_cost_ugx=Decimal(str(shipping_details['base_cost_ugx'])),
                helper_fee_ugx=Decimal(str(shipping_details['helper_fee_ugx'])),
                extra_care_fee_ugx=Decimal(str(shipping_details['extra_care_fee_ugx'])),
                total_weight_kg=Decimal(str(shipping_details['total_weight_kg'])),
                total_volume_m3=Decimal(str(shipping_details['total_volume_m3'])),
                calculation_notes={
                    'reasons': shipping_details['reasons'],
                    'requires_helper': shipping_details['requires_helper'],
                    'requires_extra_care': shipping_details['requires_extra_care'],
                },
                estimated_delivery_date=estimated_delivery_date
            )

        # Create order products and items
        for product_data in products_data:
            product_name = product_data.get('name', 'Custom Product')
            product_price = Decimal(str(product_data.get('price', 0)))
            quantity = int(product_data.get('quantity', 1))
            configuration = product_data.get('configuration', {})

            # Create OrderProduct for each product (respecting quantity)
            for _ in range(quantity):
                order_product = OrderProduct.objects.create(
                    order=order,
                    base_product_name=product_name
                )

                # Create OrderItems for each configuration part
                for part_key, part_data in configuration.items():
                    if isinstance(part_data, dict):
                        option_name = part_data.get('name', '')
                        final_price = Decimal(str(part_data.get('price', 0)))

                        # Calculate minimum payment required based on part option percentage
                        # Note: minimum_payment_percentage is stored as decimal (0.25 = 25%, 1.00 = 100%)
                        minimum_payment_required = Decimal('0.00')
                        try:
                            part_option = PartOption.objects.get(name=option_name)
                            minimum_payment_percentage = part_option.minimum_payment_percentage
                            minimum_payment_required = (final_price * minimum_payment_percentage).quantize(Decimal('0.01'))
                        except PartOption.DoesNotExist:
                            # If part option not found, default to 0
                            pass

                        OrderItem.objects.create(
                            order_product=order_product,
                            part_name=part_key.capitalize(),
                            option_name=option_name,
                            final_price=final_price,
                            minimum_payment_required=minimum_payment_required
                        )

        # Calculate minimum required amount
        order.minimum_required_amount = order.calculate_minimum_required_amount()
        order.save()

        # Serialize and return
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
