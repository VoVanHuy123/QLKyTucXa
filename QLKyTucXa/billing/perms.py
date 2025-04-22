from rest_framework import permissions
from rooms.models import RoomAssignments

class IsAdminOrUserInvoices(permissions.IsAuthenticated):
    """
    - Admin: full quyền
    - Sinh viên: chỉ được xem hóa đơn của phòng mình
    """ 
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False  # Không đăng nhập → cấm

        if user.is_staff:
            return True  # Admin được full quyền

        if request.method in permissions.SAFE_METHODS:
            # Chỉ cho GET nếu user có assignment với phòng nào đó
            return RoomAssignments.objects.filter(student=user, active=True).exists()

        return False  # Sinh viên không được POST, PUT, DELETE
    