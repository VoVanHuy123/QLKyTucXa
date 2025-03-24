from django.shortcuts import render
from rooms import perms,serializers
from KyTucXa.models import Room,Invoice
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from billing.serializers import InvoiceSerializer


# Create your views here.
#bung hết api của Room
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(status='Empty')
    serializer_class = serializers.RoomSerializer
    permission_classes = [perms.IsAdminOrReadOnly]

    @action(detail=False, methods=['get'], url_path='invoices')
    def get_invoices(self, request):
        invoices = Invoice.objects.all()
        return Response(InvoiceSerializer(invoices, many=True).data)
    