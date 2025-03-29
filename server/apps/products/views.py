from rest_framework.viewsets import ModelViewSet
from .models import Product, Part, PartOption
from .serializers import ProductSerializer, PartSerializer, PartOptionSerializer

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class PartViewSet(ModelViewSet):
    queryset = Part.objects.all()
    serializer_class = PartSerializer

class PartOptionViewSet(ModelViewSet):
    queryset = PartOption.objects.all()
    serializer_class = PartOptionSerializer
