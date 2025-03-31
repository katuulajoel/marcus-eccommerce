from rest_framework import serializers
from .models import (
    PreConfiguredProduct, 
    PreConfiguredProductParts,
    BestSellingPreconfiguredProduct,
    TopPreconfiguredProductsPerCategory
)
from apps.products.serializers import PartOptionSerializer

class PreConfiguredProductPartsSerializer(serializers.ModelSerializer):
    part_option_details = PartOptionSerializer(source='part_option', read_only=True)
    
    class Meta:
        model = PreConfiguredProductParts
        fields = '__all__'

class PreConfiguredProductSerializer(serializers.ModelSerializer):
    parts = PreConfiguredProductPartsSerializer(many=True, read_only=True)
    
    class Meta:
        model = PreConfiguredProduct
        fields = '__all__'

class BestSellingPreconfiguredProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestSellingPreconfiguredProduct
        fields = '__all__'

class TopPreconfiguredProductsPerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TopPreconfiguredProductsPerCategory
        fields = ['id', 'category_id', 'product_name', 'description', 'price', 
                  'image_url', 'times_ordered', 'preconfigured_product_id']
