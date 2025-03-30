from rest_framework.permissions import BasePermission

class AllowGetAnonymously(BasePermission):
    """
    Custom permission class to allow GET requests without authentication
    but require authentication for all other operations.
    """
    
    def has_permission(self, request, view):
        # Allow GET requests without authentication
        if request.method == 'GET':
            return True
        
        # For all other methods, require authentication
        return request.user and request.user.is_authenticated
