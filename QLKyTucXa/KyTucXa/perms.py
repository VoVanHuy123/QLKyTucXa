from rest_framework import permissions
from rest_framework import permissions
from rooms.models import RoomAssignments


class IsAuthenticatedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated


class IsAdminUser(IsAuthenticatedUser):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj) and request.user.is_staff


class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj) and request.user.is_superuser


class IsAdminOrReadOnly(IsAuthenticatedUser):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return IsAdminUser().has_permission(request, view)


class IsAdminOrUserRoomOwnerReadOnly(IsAuthenticatedUser):
    @staticmethod
    def get_user_room_ids(user):
        if hasattr(user, 'student'):
            return RoomAssignments.objects.filter(student=user.student, active=True).values_list('room_id', flat=True)
        return []

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return IsAdminUser().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return IsAdminUser().has_permission(request, view) or (
                obj.room.id in self.get_user_room_ids(request.user))


class IsAdminOrUserComplaintsOwner(IsAuthenticatedUser):
    def has_object_permission(self, request, view, obj):
        return IsAdminUser().has_permission(request, view) or obj.student.id == request.user.id


class IsObjectOwner(IsAuthenticatedUser):
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj) and obj.user == request.user


class IsStudentUser(IsAuthenticatedUser):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and hasattr(request.user, 'student')


class IsStudentOrAdminReadOnly(IsAuthenticatedUser):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return IsStudentUser().has_permission(request, view)
