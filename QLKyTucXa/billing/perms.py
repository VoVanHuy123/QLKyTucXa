from rest_framework import permissions
from rooms.models import RoomAssignments


class IsAdminOrUserInvoices(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_staff:
            return True

        if request.method in permissions.SAFE_METHODS:
            return RoomAssignments.objects.filter(student=user, active=True).exists()

        return False
