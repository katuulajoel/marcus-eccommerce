from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import F
from itertools import groupby
from operator import attrgetter
from .models import (
    PreConfiguredProduct, 
    PreConfiguredProductParts,
    BestSellingPreconfiguredProduct,
    TopPreconfiguredProductsPerCategory
)
from .serializers import (
    PreConfiguredProductSerializer, 
    PreConfiguredProductPartsSerializer,
    BestSellingPreconfiguredProductSerializer,
    TopPreconfiguredProductsPerCategorySerializer
)
from .permissions import AllowGetAnonymously

class PreConfiguredProductViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing pre-configured products
    
    Pre-configured products are complete product configurations within a category.
    
    **Authentication required**: 
    - GET: No (anyone can view pre-configured products)
    - POST, PUT, PATCH, DELETE: Yes (only authenticated users)
    """
    queryset = PreConfiguredProduct.objects.all()
    serializer_class = PreConfiguredProductSerializer
    permission_classes = [AllowGetAnonymously]
    
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
    
    **Authentication required**: 
    - GET: No (anyone can view pre-configured product parts)
    - POST, PUT, PATCH, DELETE: Yes (only authenticated users)
    """
    queryset = PreConfiguredProductParts.objects.all()
    serializer_class = PreConfiguredProductPartsSerializer
    permission_classes = [AllowGetAnonymously]
    
    def get_queryset(self):
        """Filter parts by preconfigured product if provided"""
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            queryset = queryset.filter(preconfigured_product_id=product_id)
        return queryset

class BestSellingProductView(APIView):
    """
    API endpoint that returns the best-selling preconfigured product.
    This API endpoint is open to GET requests without authentication.
    """
    permission_classes = [AllowAny]  # Allow all requests, no authentication needed
    
    def get(self, request, format=None):
        try:
            best_selling = BestSellingPreconfiguredProduct.objects.first()
            if best_selling:
                # Get the full preconfigured product details
                product = PreConfiguredProduct.objects.get(id=best_selling.preconfigured_product_id)
                serializer = PreConfiguredProductSerializer(product)
                
                # Include the analytics data
                data = serializer.data
                data['times_ordered'] = best_selling.times_ordered
                return Response(data)
            return Response({"message": "No best-selling product found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class TopProductsPerCategoryViewSet(ReadOnlyModelViewSet):
    """
    API endpoint that returns the top-selling preconfigured products per category.
    This is a read-only view that doesn't require authentication.
    
    By default, returns the top 3 preconfigured products for each category.
    Use the 'limit' query parameter to change how many products per category are returned.
    Use the 'category_id' query parameter to filter for a specific category.
    """
    queryset = TopPreconfiguredProductsPerCategory.objects.all().order_by('category_id', '-times_ordered')
    serializer_class = TopPreconfiguredProductsPerCategorySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """Allow filtering by category_id"""
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Override list method to group and limit results per category
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Check if there are any results
        if not queryset.exists():
            return Response([])
        
        # Get limit from query params, default to 3
        limit = int(request.query_params.get('limit', 3))
        
        result = []
        for category_id, group in groupby(queryset, key=attrgetter('category_id')):
            # Convert group to list and limit the number of products per category
            products = list(group)[:limit]
            # Serialize products for each category
            serialized_products = self.get_serializer(products, many=True).data
            result.extend(serialized_products)
            
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def with_details(self, request):
        """
        Return top products with full preconfigured product details
        """
        # Get basic list response first (to leverage the same grouping/limiting logic)
        response_data = self.list(request).data
        
        # Convert to list of IDs
        preconfigured_ids = [item['preconfigured_product_id'] for item in response_data]
        
        # Get the full product details
        products = PreConfiguredProduct.objects.filter(id__in=preconfigured_ids)
        
        # Create a lookup of times_ordered by preconfigured_product_id
        times_lookup = {item['preconfigured_product_id']: {
            'times_ordered': item['times_ordered'],
            'category_id': item['category_id']
        } for item in response_data}
        
        # Serialize and enrich with analytics data
        results = []
        for product in products:
            if product.id in times_lookup:
                product_data = PreConfiguredProductSerializer(product).data
                product_data['times_ordered'] = times_lookup[product.id]['times_ordered']
                product_data['category_id'] = times_lookup[product.id]['category_id']
                results.append(product_data)
        
        return Response(results)
