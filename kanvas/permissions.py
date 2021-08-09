from rest_framework.permissions import BasePermission, SAFE_METHODS

# --------------------------------------


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsInstructorAndReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_superuser


class IsFacilitador(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        if request.user.username:
            return request.user.is_staff == False and request.user.is_superuser == False

        return False
