from django.shortcuts import render
from rooms import serializers, paginators
from rooms.models import Room, Building, RoomChangeRequests
from billing.models import Invoice
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from billing.serializers import InvoiceSerializer
from rest_framework import filters
from KyTucXa import perms
from django_filters.rest_framework import DjangoFilterBackend
from .filter import RoomFilter


# Create your views here.
# bung hết api của Room
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(active = True)
    serializer_class = serializers.RoomSerializer
    permission_classes = [perms.IsAdminOrReadOnly]
    pagination_class = paginators.RoomsPaginater

    # lọc
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomFilter

    @action(detail=False, methods=['get'], url_path='invoices', permission_classes=permissions.IsAuthenticated)
    def get_invoices(self, request):
        invoices = Invoice.objects.all()
        return Response(InvoiceSerializer(invoices, many=True).data)

    @action(methods=['get'], detail=True, url_path='invoices', permission_classes=permissions.IsAuthenticated)
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
            return Response(InvoiceSerializer(invoices, many=True).data, status=status.HTTP_200_OK)


class BuidingViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = Building.objects.filter(active=True)
    serializer_class = serializers.BuildingSerializer
    permission_classes = [perms.IsAdminOrReadOnly]


class RoomChangeRequestViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView,
                               generics.UpdateAPIView):
    queryset = RoomChangeRequests.objects.filter(active=True)
    serializer_class = serializers.RoomChangeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
