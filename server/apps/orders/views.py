from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Orders, OrderProduct, OrderItem
from .serializers import OrdersSerializer, OrderProductSerializer, OrderItemSerializer

class OrdersViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing orders.
    
    **Authentication required**: Yes
    
    Only authenticated users can access this endpoint.
    Regular users can only see their own orders.
    Staff users can see all orders.
    """
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer
    permission_classes = [IsAuthenticated]
    
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
