from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Part, PartOption, Stock
from .serializers import CategorySerializer, PartSerializer, PartOptionSerializer, StockSerializer
from .permissions import AllowGetAnonymously

class CategoryViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing categories
    
    **Authentication required**: 
    - GET: No (anyone can view categories)
    - POST, PUT, PATCH, DELETE: Yes (only authenticated users)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowGetAnonymously]
    
    @action(detail=True, methods=['get'])
    def parts(self, request, pk=None):
        """Get all parts for a specific category"""
        category = self.get_object()
        parts = Part.objects.filter(category=category)
        serializer = PartSerializer(parts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """Get stock information for all parts in this category"""
        category = self.get_object()
        
        # Get all part options for this category
        parts = Part.objects.filter(category=category)
        part_ids = [part.id for part in parts]
        part_options = PartOption.objects.filter(part_id__in=part_ids)
        option_ids = [option.id for option in part_options]
        
        # Get stock for these part options
        stocks = Stock.objects.filter(part_option_id__in=option_ids)
        serializer = StockSerializer(stocks, many=True)
        
        return Response(serializer.data)

class PartViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing parts
    
    **Authentication required**: 
    - GET: No (anyone can view parts)
    - POST, PUT, PATCH, DELETE: Yes (only authenticated users)
    """
    queryset = Part.objects.all()
    serializer_class = PartSerializer
    permission_classes = [AllowGetAnonymously]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
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

    **Authentication required**:
    - GET: No (anyone can view part options)
    - POST, PUT, PATCH, DELETE: Yes (only authenticated users)
    """
    queryset = PartOption.objects.all()
    serializer_class = PartOptionSerializer
    permission_classes = [AllowGetAnonymously]

    def get_queryset(self):
        queryset = super().get_queryset()
        part_id = self.request.query_params.get('part_id', None)
        if part_id:
            queryset = queryset.filter(part_id=part_id)
        return queryset

    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        """Get stock information for this part option"""
        part_option = self.get_object()
        stocks = Stock.objects.filter(part_option=part_option)
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)

class StockViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing stock levels
    
    **Authentication required**: 
    - GET: No (anyone can view stock levels)
    - POST, PUT, PATCH, DELETE: Yes (only authenticated users)
    """
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [AllowGetAnonymously]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        part_option_id = self.request.query_params.get('part_option_id', None)
        if part_option_id:
            queryset = queryset.filter(part_option_id=part_option_id)
        return queryset
