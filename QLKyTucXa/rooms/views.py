from django.shortcuts import render
from rooms import perms, serializers, paginators
from rooms.models import Room, Building, RoomChangeRequests,RoomAssignments
from billing.models import Invoice
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from billing.serializers import InvoiceSerializer
from rest_framework import filters
from KyTucXa import perms
from django_filters.rest_framework import DjangoFilterBackend
from .filter import RoomFilter
from billing.paginators import InvoicePaginater
from account.models import Student


# Create your views here.
# bung hết api của Room
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(active = True).order_by('room_number')
    serializer_class = serializers.RoomSerializer
    permission_classes = [perms.IsAdminOrReadOnly]
    pagination_class = paginators.RoomsPaginater

    # lọc
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomFilter

    @action(detail=False, methods=['get'], url_path='invoices', permission_classes=[permissions.IsAuthenticated])
    def get_invoices(self, request):
        invoices = Invoice.objects.all()
        return Response(InvoiceSerializer(invoices, many=True).data)

    @action(methods=['get'], detail=True, url_path='invoices', permission_classes=[permissions.IsAuthenticated])
    def get_room_invoices(self, request, pk):
        # /romms/{id}/invocies/{id}
        invoice_id = request.query_params.get('invoice_id', None)
        if invoice_id:
            try:
                invoice = Invoice.objects.get(id=invoice_id, room_id=pk)
                return Response(InvoiceSerializer(invoice).data, status=status.HTTP_200_OK)
            except Invoice.DoesNotExist:
                return Response({"error": "Invoice not found for this room"}, status=status.HTTP_404_NOT_FOUND)
        else:  # nếu không có invoice_id thì lấy danh sách invoices
            invoices = Invoice.objects.filter(room_id=pk)
            paginator = InvoicePaginater()
            page = paginator.paginate_queryset(invoices, request)
            if page is not None:
                serializer = InvoiceSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            return Response(InvoiceSerializer(invoices, many=True).data, status=status.HTTP_200_OK)
    @action(methods=['post'], detail=True, url_path='register-member', permission_classes=[permissions.IsAdminUser])
    def register_member(self, request, pk):
        try:
            room = Room.objects.get(pk=pk, active=True)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        if room.available_beds <= 0:
            return Response({"error": "Phòng đã đầy"}, status=status.HTTP_400_BAD_REQUEST)

        student_id = request.data.get("student_id")
        bed_number = request.data.get("bed_number")

        if not student_id or bed_number is None:
            return Response({"error": "Thiếu thông tin sinh viên hoặc số giường"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Sinh viên không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        if RoomAssignments.objects.filter(room=room, bed_number=bed_number, active=True).exists():
            return Response({"error": f"Giường số {bed_number} đã có người đăng ký"}, status=status.HTTP_400_BAD_REQUEST)

        if RoomAssignments.objects.filter(student=student, active=True).exists():
            return Response({"error": "Sinh viên đã ở một phòng khác!"}, status=400)

        assignment = RoomAssignments.objects.create(
            room=room,
            student=student,
            bed_number=bed_number,
            active=True
        )

        room.available_beds -= 1
        if room.available_beds == 0:
            room.status = 'Full'
        room.save()

        return Response(serializers.RoomAssignmentsSerializer(assignment).data, status=status.HTTP_201_CREATED)


class BuidingViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = Building.objects.filter(active=True)
    serializer_class = serializers.BuildingSerializer
    permission_classes = [perms.IsAdminOrReadOnly]


class RoomChangeRequestViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView,
                               generics.UpdateAPIView):
    queryset = RoomChangeRequests.objects.filter(active=True)
    serializer_class = serializers.RoomChangeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

class RoomAssignmentsViewSet(viewsets.ViewSet,generics.RetrieveAPIView,generics.UpdateAPIView):
    queryset = RoomAssignments.objects.filter(active=True)
    serializer_class = serializers.RoomAssignmentsSerializer
    permission_classes = [permissions.IsAdminUser]
