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
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'room','description', 'total_amount', 'status', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # lấy và loại bỏ "items" khỏi validated_data
        invoice = Invoice.objects.create(**validated_data)  # tạo hóa đơn
        for item_data in items_data:
            InvoiceItems.objects.create(invoice=invoice, **item_data)  # tạo từng khoản và gắn vào hóa đơn
        return invoice
