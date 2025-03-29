from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Part, PartOption, Stock
from .serializers import ProductSerializer, PartSerializer, PartOptionSerializer, StockSerializer

class ProductViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing products
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class PartViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing parts
    """
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
    
    @action(detail=True, methods=['get'])
    def options(self, request, pk=None):
        """Get all options for a specific part"""
        part = self.get_object()
        options = PartOption.objects.filter(part=part)
        serializer = PartOptionSerializer(options, many=True)
        return Response(serializer.data)

class PartOptionViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing part options
    """
    queryset = PartOption.objects.all()
    serializer_class = PartOptionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        part_id = self.request.query_params.get('part_id', None)
        if part_id:
            queryset = queryset.filter(part_id=part_id)
        return queryset

class StockViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing stock levels
    """
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        part_option_id = self.request.query_params.get('part_option_id', None)
        if part_option_id:
            queryset = queryset.filter(part_option_id=part_option_id)
        return queryset
