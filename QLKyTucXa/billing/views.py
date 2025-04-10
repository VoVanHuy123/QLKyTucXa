
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets,generics,permissions
from billing.models import Invoice
from billing.serializers import InvoiceSerializer


# Create your views here.
class InvoiceViewSet(viewsets.ViewSet,generics.CreateAPIView,generics.RetrieveAPIView,generics.ListAPIView):
    queryset = Invoice.objects.filter(active = True)
    serializer_class = InvoiceSerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]  # Chỉ Admin mới được tạo
        return [permissions.IsAuthenticated()]  # Còn lại chỉ cần đăng nhập