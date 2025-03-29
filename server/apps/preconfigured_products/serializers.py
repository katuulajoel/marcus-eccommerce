from rest_framework import serializers
from .models import PreConfiguredProduct, PreConfiguredProductParts
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
