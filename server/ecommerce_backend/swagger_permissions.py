from rest_framework import permissions

class SwaggerPermission(permissions.BasePermission):
    """
    Custom permission class for Swagger UI.
    - Allow all users to see non-sensitive endpoints
    - Require authentication for sensitive endpoints
    """
    
    def has_permission(self, request, view):
        # Allow all users to see the schema for non-sensitive endpoints
        path = request.path_info
        
        # Block unauthenticated users from seeing order endpoints in schema
        if 'orders' in path and not request.user.is_authenticated:
            return False
        
        # Allow access to others
        return True
