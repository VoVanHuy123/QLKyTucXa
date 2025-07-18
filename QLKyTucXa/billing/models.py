from django.db import models
from django_mysql.models import EnumField

from KyTucXa.models import BaseModel
from rooms.models import Room

class InvoiceStatus(models.TextChoices):
    UNPAID = 'Unpaid', 'Unpaid'
    PAID = 'Paid', 'Paid'

class Invoice(BaseModel):
    description = models.CharField(max_length=100, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    invoice_month = models.DateField()
    total_amount = models.FloatField()
    status = EnumField(choices=InvoiceStatus.choices, default=InvoiceStatus.UNPAID)

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
