from rest_framework.permissions import BasePermission, SAFE_METHODS

# --------------------------------------


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsFacilitador(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff
