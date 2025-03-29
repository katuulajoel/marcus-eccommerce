from rest_framework import serializers
from .models import Orders, OrderProduct, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderProductSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = OrderProduct
        fields = '__all__'

class OrdersSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Orders
        fields = '__all__'
