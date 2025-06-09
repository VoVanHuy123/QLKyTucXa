from datetime import datetime

from django.contrib import admin
from django.db import models
from django.db.models import Sum, Q, FloatField
from django.db.models.functions import Coalesce
from django.forms import formset_factory
from django.template.response import TemplateResponse
from django.urls import path

from config.PushNoti import send_push_notification
from rooms.models import Room, Building, RoomChangeRequests, RoomAssignments
from billing.models import Invoice, InvoiceItems, InvoiceStatus
from account.models import User, Student
from support.models import Complaints, ComplaintsResponse
from surveys.models import Survey, SurveyResponse, SurveyQuestion
from notifications.models import Notification
from billing.forms import InvoiceInputForm
from django.shortcuts import redirect
from django.contrib import messages


class MyAdminSite(admin.AdminSite):
    site_header = "Quản lý ký túc xá"
    site_title = "Quản lý ký túc xá"
    index_title = "Chào mừng đến với trang quản trị"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add-invoice/', self.add_invoice_view, name='add-invoice'),
            path('revenue-stats/', self.stats_view, name='revenue-stats'),
        ]
        return custom_urls + urls

    def add_invoice_view(self, request):
        InvoiceFormSet = formset_factory(InvoiceInputForm, extra=0)

        if request.method == 'POST':
            month_str = request.POST.get('month')
        else:
            month_str = request.GET.get('month')

        try:
            month_date = datetime.strptime(month_str, '%Y-%m') if month_str else datetime.now()
        except ValueError:
            month_date = datetime.now()

        if request.method == 'POST':
            formset = InvoiceFormSet(request.POST)
            if formset.is_valid():
                created_count = 0
                skipped_rooms = 0

                for form in formset:
                    room_id = form.cleaned_data.get('room_id')
                    electricity_fee = form.cleaned_data.get('electricity_fee')
                    water_fee = form.cleaned_data.get('water_fee')
                    other_services_fee = form.cleaned_data.get('other_services_fee') or 0

                    try:
                        room = Room.objects.get(id=room_id)
                    except Room.DoesNotExist:
                        continue

                    if Invoice.objects.filter(room=room, invoice_month__year=month_date.year,
                                              invoice_month__month=month_date.month).exists():
                        skipped_rooms += 1
                        continue

                    room_fee = room.monthly_fee
                    total_amount = room_fee + electricity_fee + water_fee + other_services_fee
                    description = f"Hóa đơn {month_date.strftime('%m/%Y')} - Phòng {room.room_number}"

                    invoice = Invoice.objects.create(
                        description=description,
                        room=room,
                        total_amount=total_amount,
                        status=InvoiceStatus.UNPAID,
                        active=False,
                        invoice_month=month_date.date()
                    )

                    items = [
                        InvoiceItems(invoice=invoice, description="Tiền nhà", amount=room_fee),
                        InvoiceItems(invoice=invoice, description="Tiền điện", amount=electricity_fee),
                        InvoiceItems(invoice=invoice, description="Tiền nước", amount=water_fee),
                    ]
                    if other_services_fee > 0:
                        items.append(
                            InvoiceItems(invoice=invoice, description="Dịch vụ khác", amount=other_services_fee))

                    InvoiceItems.objects.bulk_create(items)
                    created_count += 1

                if created_count > 0:
                    messages.success(request, f"Đã tạo {created_count} hóa đơn mới.")
                if skipped_rooms > 0:
                    messages.warning(request, f"Bỏ qua {skipped_rooms} phòng vì đã có hóa đơn trong tháng.")

                return redirect(f"{request.path}?month={month_date.strftime('%Y-%m')}")
            else:
                print("Formset errors:", formset.errors)
                print("Non-form errors:", formset.non_form_errors())

        else:
            rooms = Room.objects.filter(available_beds__lt=models.F('total_beds')).order_by(
                'building__building_name', 'floor', 'room_number'
            )
            initial_data = [{
                'room_id': room.id,
                'room_name': f"{room.building.building_name} - Tầng {room.floor} - {room.room_number}",
                'monthly_fee': room.monthly_fee,
                'electricity_fee': 0,
                'water_fee': 0,
                'other_services_fee': 0,
            } for room in rooms]

            formset = InvoiceFormSet(initial=initial_data)

        context = dict(
            self.each_context(request),
            title="Nhập hóa đơn",
            formset=formset,
            month=month_date.strftime('%Y-%m')
        )
        return TemplateResponse(request, "admin/add-invoice.html", context)

    def stats_view(self, request):
        revenue_stats = []
        months = [f"{i:02d}" for i in range(1, 13)]
        context = self.each_context(request)

        year = request.GET.get('year')
        month = request.GET.get('month')
        quarter = request.GET.get('quarter')

        if year or month or quarter:
            building_filters = Q(rooms__invoice__status=InvoiceStatus.PAID)
            invoice_filters = Q(status=InvoiceStatus.PAID)

            if year:
                building_filters &= Q(rooms__invoice__created_date__year=year)
                invoice_filters &= Q(created_date__year=year)

            if quarter:
                quarter_to_months = {
                    'Q1': [1, 2, 3],
                    'Q2': [4, 5, 6],
                    'Q3': [7, 8, 9],
                    'Q4': [10, 11, 12],
                }
                months_for_quarter = quarter_to_months.get(quarter)
                if months_for_quarter:
                    building_filters &= Q(rooms__invoice__created_date__month__in=months_for_quarter)
                    invoice_filters &= Q(created_date__month__in=months_for_quarter)

            elif month:
                building_filters &= Q(rooms__invoice__created_date__month=month)
                invoice_filters &= Q(created_date__month=month)

            per_building_totals = Building.objects.annotate(
                total_amount=Coalesce(
                    Sum('rooms__invoice__total_amount', filter=building_filters, output_field=FloatField()),
                    0.0,
                    output_field=FloatField()
                )
            ).values('building_name', 'total_amount').order_by('building_name')

            overall_total = Invoice.objects.filter(invoice_filters).aggregate(
                total=Sum('total_amount', output_field=FloatField())
            )

            summary_row = {
                'building_name': 'Tổng',
                'total_amount': overall_total['total']
            }

            revenue_stats = list(per_building_totals) + [summary_row]

        context.update({
            'title': 'Thống kê doanh thu',
            'revenue_stats': revenue_stats,
            'months': months,
            'year': year or '',
            'month': month or '',
            'quarter': quarter or ''
        })

        return TemplateResponse(request, 'admin/revenue-stats.html', context)


###
class StudentInline(admin.StackedInline):
    model = Student
    extra = 0
    fields = ("student_code", "university")


class MyUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-id",)
    inlines = [StudentInline]

    def save_form(self, request, form, change):
        user = super().save_form(request, form, change)
        if user.password and (user.pk is None or user.password != form.initial.get('password')):
            user.set_password(user.password)
        return user

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


class StudentRoomInline(admin.TabularInline):
    model = RoomAssignments
    fk_name = 'student'
    extra = 1


class MyStudentAdmin(admin.ModelAdmin):
    list_display = ("student_code", "university", "first_name", "last_name")
    list_filter = ("university",)
    search_fields = ("university", "first_name", "last_name")
    ordering = ("-id",)
    inlines = [StudentRoomInline]

    def save_form(self, request, form, change):
        user = super().save_form(request, form, change)
        if user.password and (user.pk is None or user.password != form.initial.get('password')):
            user.set_password(user.password)
        return user

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


###
class InvoiceItemInline(admin.StackedInline):
    model = InvoiceItems
    extra = 1


class MyInvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "total_amount", "status", "invoice_month", "active")
    list_filter = ("room_id", "status")
    search_fields = ("room__room_number", "total_amount")
    inlines = [InvoiceItemInline]


###
class MyBuildingAdmin(admin.ModelAdmin):
    list_display = ("building_name", "total_floors", "active")
    list_filter = ("total_floors", "active")
    search_fields = ("building_name", "total_floors")


class RoomStudentInline(admin.TabularInline):
    model = RoomAssignments
    fk_name = 'room'
    extra = 1


class MyRoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_type", "floor", "total_beds", "building", "available_beds", "active")
    list_filter = ("room_type", "floor", "building", "status")
    search_fields = ("room_number", "total_beds")
    inlines = [RoomStudentInline]


class MyRoomChangeRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "student_code", "current_room_name", "requested_room_name", "status")
    list_filter = ("current_room", "requested_room", "status")
    search_fields = ("student__student_code", "current_room__room_number", "requested_room__room_number")

    def student_code(self, obj):
        return obj.student.student_code

    def current_room_name(self, obj):
        return obj.current_room.room_number

    def requested_room_name(self, obj):
        return obj.requested_room.room_number


###
class ComplaintResponseInline(admin.StackedInline):
    model = ComplaintsResponse
    extra = 1


class MyComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "student_name", "room", "title", "status")
    list_filter = ("room_id", "status")
    search_fields = ("room__room_number", "title", "description")
    inlines = [ComplaintResponseInline]

    def student_name(self, obj):
        return obj.student.student_code


###
class SurveyQuestionInline(admin.StackedInline):
    model = SurveyQuestion
    extra = 1


class SurveyResponseInline(admin.TabularInline):
    model = SurveyResponse
    extra = 0


class MySurveyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "user", "created_date", "update_date", "active")
    list_filter = ("active",)
    search_fields = ("title", "description")
    ordering = ("-created_date",)
    inlines = [SurveyQuestionInline, SurveyResponseInline]


class MySurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "survey_id", "question_type", "created_date", "update_date")
    list_filter = ("question_type",)
    search_fields = ("question_text", "survey__title")
    ordering = ("-created_date",)


class MySurveyResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "survey_id", "question_id", "student", "created_date", "update_date")
    list_filter = ("question__question_type",)
    search_fields = ("student__student_code", "question__question_text", "answer")
    ordering = ("-created_date",)


###
class MyNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "content", "announcement_type", "is_urgent")
    list_filter = ("announcement_type",)
    search_fields = ("title", "content")
    ordering = ("-created_date",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.is_urgent:
            users = User.objects.exclude(expo_token=None).exclude(expo_token="")
            for user in users:
                send_push_notification(user.expo_token, obj.title, obj.content)


###
class MyRoomAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "student_name", "bed_number")
    list_filter = ("room",)
    search_fields = ("student__first_name", "student__last_name")
    ordering = ("room", "student")

    def student_name(self, obj):
        return obj.student.first_name + ' ' + obj.student.last_name


admin_site = MyAdminSite(name='myadmin')
admin_site.register(User, MyUserAdmin)
admin_site.register(Student, MyStudentAdmin)
admin_site.register(Room, MyRoomAdmin)
admin_site.register(Invoice, MyInvoiceAdmin)
admin_site.register(Building, MyBuildingAdmin)
admin_site.register(RoomChangeRequests, MyRoomChangeRequestAdmin)
admin_site.register(Complaints, MyComplaintAdmin)
admin_site.register(Survey, MySurveyAdmin)
admin_site.register(SurveyQuestion, MySurveyQuestionAdmin)
admin_site.register(SurveyResponse, MySurveyResponseAdmin)
admin_site.register(RoomAssignments, MyRoomAssignmentAdmin)
admin_site.register(Notification, MyNotificationAdmin)
