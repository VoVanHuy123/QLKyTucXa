from django.db import models
from KyTucXa.models import BaseModel
from rooms.models import Room


class Invoice(BaseModel):
    STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid')
    ]
    description = models.CharField(max_length=100, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    # amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return self.description

    class Meta:
        db_table = "invoice"


class InvoiceItems(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE,related_name="items")
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.description

    class Meta:
        db_table = "invoice_items"
