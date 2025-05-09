from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, generics, permissions, status
from billing.models import Invoice
from billing.serializers import InvoiceSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filter import InvoicesFilter
from .paginators import InvoicePaginater
from .perms import IsAdminOrUserInvoices
from KyTucXa.perms import IsAdminOrUserRoomOwnerReadOnly
from rooms.models import RoomAssignments


class InvoiceViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView,
                     generics.ListAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Invoice.objects.filter(active=True).order_by('-id')
    serializer_class = InvoiceSerializer
    pagination_class = InvoicePaginater
    filter_backends = [DjangoFilterBackend]
    filterset_class = InvoicesFilter
    permission_classes = [IsAdminOrUserRoomOwnerReadOnly]

    @action(detail=False, methods=['get'], url_path='my-room-invoices')
    def my_room_invoices(self, request):
        user = request.user

        if not hasattr(user, 'student') or request.user.student is None:
            return Response({"error": "Tài khoản không liên kết với sinh viên."},
                            status=status.HTTP_400_BAD_REQUEST)

        assignment = RoomAssignments.objects.get(student=user.student, active=True)
        invoices = self.queryset().filter(room=assignment.room)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(invoices, request)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
