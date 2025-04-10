from rest_framework import serializers
from billing.models import Invoice, InvoiceItems
from rooms.serializers import RoomSerializer

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItems
        fields = ['id', 'description', 'amount']

class InvoiceSerializer(serializers.ModelSerializer):
    room=RoomSerializer
    #lấy serializer của các item
    items = InvoiceItemSerializer(many=True, source='invoiceitems_set', read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'room', 'total_amount', 'status', 'items']
