from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    - Cho phép tất cả user đăng nhập (IsAuthenticated) truy cập `retrieve` (GET)
    - Chỉ cho phép admin cập nhật (PUT, PATCH) hoặc xóa (DELETE)
    """
    def has_permission(self, request, view):
        # Ai cũng có thể truy cập nếu là GET (retrieve) or (list)
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated  
        # Các phương thức PUT, PATCH, DELETE chỉ cho admin
        return request.user and request.user.is_authenticated and request.user.role == "admin"