from rest_framework import serializers
from .models import Product, Part, PartOption

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = '__all__'

class PartOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartOption
        fields = '__all__'
