from rest_framework.viewsets import ModelViewSet
from .models import Order, OrderProduct
from .serializers import OrderSerializer, OrderProductSerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderProductViewSet(ModelViewSet):
    queryset = OrderProduct.objects.all()
    serializer_class = OrderProductSerializer
