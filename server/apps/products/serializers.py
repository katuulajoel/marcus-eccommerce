from rest_framework import serializers
from .models import Category, Part, PartOption, Stock

class PartOptionSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part.name', read_only=True)

    class Meta:
        model = PartOption
        fields = '__all__'

class PartSerializer(serializers.ModelSerializer):
    options = PartOptionSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Part
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    parts = PartSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
