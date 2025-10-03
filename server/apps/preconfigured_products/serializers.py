from rest_framework import serializers
from django.conf import settings
from .models import (
    PreConfiguredProduct, 
    PreConfiguredProductParts,
    BestSellingPreconfiguredProduct,
    TopPreconfiguredProductsPerCategory
)
from apps.products.serializers import PartOptionSerializer
from apps.products.models import Category

class PreConfiguredProductPartsSerializer(serializers.ModelSerializer):
    part_option_details = PartOptionSerializer(source='part_option', read_only=True)
    
    class Meta:
        model = PreConfiguredProductParts
        fields = '__all__'

class CategoryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class PreConfiguredProductSerializer(serializers.ModelSerializer):
    parts = PreConfiguredProductPartsSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    category_details = CategoryDetailsSerializer(source='category', read_only=True)
    part_options = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of part option IDs to associate with this preconfigured product"
    )

    class Meta:
        model = PreConfiguredProduct
        fields = '__all__'

    def get_image_url(self, obj):
        """Return full URL for image if it exists."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def create(self, validated_data):
        """Create preconfigured product and associate part options"""
        part_option_ids = validated_data.pop('part_options', [])

        # Create the preconfigured product
        product = PreConfiguredProduct.objects.create(**validated_data)

        # Create the associated parts
        for part_option_id in part_option_ids:
            PreConfiguredProductParts.objects.create(
                preconfigured_product=product,
                part_option_id=part_option_id
            )

        return product

    def update(self, instance, validated_data):
        """Update preconfigured product and optionally update part options"""
        part_option_ids = validated_data.pop('part_options', None)

        # Update the product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If part_options are provided, replace existing parts
        if part_option_ids is not None:
            # Delete existing parts
            PreConfiguredProductParts.objects.filter(preconfigured_product=instance).delete()

            # Create new parts
            for part_option_id in part_option_ids:
                PreConfiguredProductParts.objects.create(
                    preconfigured_product=instance,
                    part_option_id=part_option_id
                )

        return instance

class BestSellingPreconfiguredProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestSellingPreconfiguredProduct
        fields = '__all__'

    def get_image_url(self, obj):
        """Return full URL for image if it exists."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class TopPreconfiguredProductsPerCategorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='preconfigured_name')
    
    class Meta:
        model = TopPreconfiguredProductsPerCategory
        fields = ['category_id', 'product_name', 'times_ordered', 'preconfigured_product_id']
    
    def get_image_url(self, obj):
        """Return full URL for image if it exists."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
