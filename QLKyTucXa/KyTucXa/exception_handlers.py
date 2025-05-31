from rest_framework.views import exception_handler
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, PermissionDenied):
        return Response({'error': 'Bạn không có quyền truy cập chức năng này.'},
                        status=status.HTTP_403_FORBIDDEN)

    if isinstance(exc, NotAuthenticated):
        return Response({'error': 'Bạn cần đăng nhập để thực hiện hành động này.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    return response
