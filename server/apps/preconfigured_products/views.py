from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PreConfiguredProduct, PreConfiguredProductParts
from .serializers import PreConfiguredProductSerializer, PreConfiguredProductPartsSerializer

class PreConfiguredProductViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing pre-configured products
    """
    queryset = PreConfiguredProduct.objects.all()
    serializer_class = PreConfiguredProductSerializer
    
    @action(detail=True, methods=['get'])
    def parts(self, request, pk=None):
        """Get all parts for a specific preconfigured product"""
        product = self.get_object()
        parts = PreConfiguredProductParts.objects.filter(preconfigured_product=product)
        serializer = PreConfiguredProductPartsSerializer(parts, many=True)
        return Response(serializer.data)

class PreConfiguredProductPartsViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing pre-configured product parts
    """
    queryset = PreConfiguredProductParts.objects.all()
    serializer_class = PreConfiguredProductPartsSerializer
    
    def get_queryset(self):
        """Filter parts by preconfigured product if provided"""
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(preconfigured_product_id=product_id)
        return queryset
