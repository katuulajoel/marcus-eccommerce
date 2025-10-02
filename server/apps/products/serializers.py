from rest_framework import serializers
from .models import Category, Part, PartOption, Stock


class PartOptionSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part.name', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PartOption
        fields = '__all__'

    def get_image_url(self, obj):
        """Return full URL for image if it exists."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class PartSerializer(serializers.ModelSerializer):
    options = PartOptionSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Part
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    parts = PartSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_image_url(self, obj):
        """Return full URL for image if it exists."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
