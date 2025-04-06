from django.contrib import admin
from rooms.models import Room, Building
from billing.models import Invoice,InvoiceItems


# Register your models here.
admin_site = admin
admin.site.register(Room)
admin.site.register(Building)
admin.site.register(Invoice)
admin.site.register(InvoiceItems)