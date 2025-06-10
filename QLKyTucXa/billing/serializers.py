from rest_framework import serializers
from billing.models import Invoice, InvoiceItems
from rooms.serializers import RoomSerializer
from rooms.models import Room


class InvoiceItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = InvoiceItems
        fields = ['id', 'description', 'amount']


class InvoiceSerializer(serializers.ModelSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all())
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'room', 'description', 'total_amount', 'status', 'items', 'created_date']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItems.objects.create(invoice=invoice, **item_data)
        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        instance = super().update(instance, validated_data)

        existing_items = {item.id: item for item in instance.items.all()}
        sent_item_ids = [item.get('id') for item in items_data if item.get('id')]

        for item_id, item in existing_items.items():
            if item_id not in sent_item_ids:
                item.delete()

        for item_data in items_data:
            item_id = item_data.get('id')
            if item_id and item_id in existing_items:
                item = existing_items[item_id]
                for attr, value in item_data.items():
                    setattr(item, attr, value)
                item.save()
            else:
                InvoiceItems.objects.create(invoice=instance, **item_data)

        return instance
