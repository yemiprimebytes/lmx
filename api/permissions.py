from rest_framework import permissions

class IsAdminOrLecturer(permissions.BasePermission):
    """
    Custom permission to only allow Admins or Lecturers to edit/create content.
    """
    def has_permission(self, request, view):
        # Allow safe methods (GET, HEAD, OPTIONS) for any user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow if user is an Admin (superuser) or a Lecturer
        return bool(request.user.is_superuser or request.user.is_lecturer)
    

class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Allows read-only access to any user, but restricts
    modifications to superusers only.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, or OPTIONS requests for any user [cite: 64]
        if request.method in permissions.SAFE_METHODS:
            return True

        # Restrict POST, PUT, PATCH, DELETE to superusers only 
        return bool(request.user and request.user.is_superuser)
    

class IsLecturerOrReadOnly(permissions.BasePermission):
    """
    Allow Students to view (GET), but only Lecturers/Admins 
    to Create, Update, or Delete.
    """
    def has_permission(self, request, view):
        # Allow anyone to view the list or details
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user is logged in
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow access if the user is a Lecturer or an Admin
        return bool(request.user.is_lecturer)