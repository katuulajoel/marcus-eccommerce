from rest_framework.viewsets import ModelViewSet, ViewSet
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
from apps.products.models import Category

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
                data['image_url'] = product.image_url
                data['description'] = product.description  # Include product description
                
                # Include part options with descriptions
                parts = PreConfiguredProductParts.objects.filter(preconfigured_product=product)
                parts_data = []
                for part in parts:
                    part_data = PreConfiguredProductPartsSerializer(part).data
                    part_option = part.part_option
                    if part_option:
                        part_data['part_option_details']['description'] = part_option.description  # Include part option description
                    parts_data.append(part_data)
                data['parts'] = parts_data
                
                return Response(data)
            return Response({"message": "No best-selling product found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class TopProductsPerCategoryViewSet(ViewSet):
    """
    API endpoint that returns the top-selling preconfigured products per category.
    This is a read-only view that doesn't require authentication.
    
    Returns the top preconfigured products for each category with full product details.
    Use the 'limit' query parameter to change how many products per category are returned (default: 3).
    Use the 'category_id' query parameter to filter for a specific category.
    """
    permission_classes = [AllowAny]
    
    def list(self, request):
        """
        Return top products with full preconfigured product details
        """
        # Get limit from query params, default to 3
        limit = int(request.query_params.get('limit', 3))
        
        # Get the base queryset
        queryset = TopPreconfiguredProductsPerCategory.objects.all().order_by('category_id', '-times_ordered')
        
        # Filter by category if needed
        category_id = request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Check if there are any results
        if not queryset.exists():
            return Response([])
        
        # Group by category and limit results
        result = []
        preconfigured_ids = []
        category_data = {}
        category_ids = set()
        
        for category_id, group in groupby(queryset, key=attrgetter('category_id')):
            # Convert group to list and limit the number of products per category
            products = list(group)[:limit]
            category_ids.add(category_id)
            
            # Store analytics data for each product
            for product in products:
                preconfigured_ids.append(product.preconfigured_product_id)
                category_data[product.preconfigured_product_id] = {
                    'times_ordered': product.times_ordered,
                    'category_id': product.category_id
                }
        
        # Get the full product details
        products = PreConfiguredProduct.objects.filter(id__in=preconfigured_ids)
        
        # Get category details
        categories = {category.id: category for category in Category.objects.filter(id__in=category_ids)}
        
        # Serialize and enrich with analytics data and category details
        results = []
        for product in products:
            if product.id in category_data:
                product_data = PreConfiguredProductSerializer(product).data
                product_data['times_ordered'] = category_data[product.id]['times_ordered']
                product_data['image_url'] = product.image_url
                product_data['description'] = product.description  # Include product description
                
                # Add category details
                cat_id = category_data[product.id]['category_id']
                product_data['category_id'] = cat_id
                product_data['category_details'] = {
                    'id': cat_id,
                    'name': categories[cat_id].name,
                    'description': categories[cat_id].description if hasattr(categories[cat_id], 'description') else None,
                    'slug': categories[cat_id].slug if hasattr(categories[cat_id], 'slug') else None
                }
                
                # Include part options with descriptions
                parts = PreConfiguredProductParts.objects.filter(preconfigured_product=product)
                parts_data = []
                for part in parts:
                    part_data = PreConfiguredProductPartsSerializer(part).data
                    part_option = part.part_option
                    if part_option:
                        part_data['part_option_details']['description'] = part_option.description  # Include part option description
                    parts_data.append(part_data)
                product_data['parts'] = parts_data
                
                results.append(product_data)
        
        return Response(results)
