from rest_framework import serializers
from .models import Product, Part, PartOption

class PartOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartOption
        fields = '__all__'

class PartSerializer(serializers.ModelSerializer):
    options = PartOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Part
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    parts = PartSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
