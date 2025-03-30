from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Customer
from .serializers import CustomerSerializer

class CustomerViewSet(ModelViewSet):
    """
    API endpoint for viewing and editing customers.
    
    **Authentication required**: Yes
    
    Only authenticated users can access this endpoint.
    Regular users can only see their own customer profile.
    Staff users can see all customer profiles.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter customers to return only the current user's customer profile
        if the user is not a staff member
        """
        queryset = Customer.objects.all()
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            # If a regular user is logged in, only show their customer profile
            queryset = queryset.filter(user=self.request.user)
        return queryset
