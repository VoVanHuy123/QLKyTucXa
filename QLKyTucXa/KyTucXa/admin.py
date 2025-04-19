from django.contrib import admin
from rooms.models import Room, Building
from billing.models import Invoice,InvoiceItems
from account.models import User

class MyUserAdmin(admin.ModelAdmin):
    search_fields = ["first_name"]

    def save_form(self, request, form, change):
        data = super().save_form(request, form, change)
        data.set_password(data.password)
        return data

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)



# Register your models here.
admin_site = admin
admin.site.register(Room)
admin.site.register(Building)
admin.site.register(Invoice)
admin.site.register(InvoiceItems)
admin.site.register(User, MyUserAdmin)