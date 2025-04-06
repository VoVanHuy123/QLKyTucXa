from rest_framework import serializers
from billing.models import Invoice, InvoiceItems

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItems
        fields = ['id', 'description', 'amount']

class InvoiceSerializer(serializers.ModelSerializer):
    #lấy serializer của các item
    items = InvoiceItemSerializer(many=True, source='invoiceitems_set', read_only=True)

    class Meta:
        model = Invoice
        fields = ['id', 'room', 'total_amount', 'status', 'items']
