from rest_framework.permissions import BasePermission

class AllowPostAnonymously(BasePermission):
    """
    Custom permission class to allow POST requests without authentication
    but require authentication for all other operations.
    """
    
    def has_permission(self, request, view):
        # Allow POST requests without authentication
        if request.method == 'POST':
            return True
        
        # For all other methods, require authentication
        return request.user and request.user.is_authenticated
