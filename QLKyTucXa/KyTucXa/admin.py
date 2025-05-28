from django.contrib import admin
from django.db.models import Sum, Q, FloatField
from django.db.models.functions import  Coalesce
from django.template.response import TemplateResponse
from django.urls import path

from rooms.models import Room, Building, RoomChangeRequests, RoomAssignments
from billing.models import Invoice, InvoiceItems, InvoiceStatus
from account.models import User, Student
from support.models import Complaints, ComplaintsResponse
from surveys.models import Survey, SurveyResponse, SurveyQuestion
from notifications.models import Notification


class MyAdminSite(admin.AdminSite):
    site_header = "Quản lý ký túc xá"
    site_title = "Quản lý ký túc xá"
    index_title = "Chào mừng đến với trang quản trị"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('revenue-stats/', self.stats_view, name='revenue-stats')
        ]
        return custom_urls + urls

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
    extra = 1


class MyUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("-id",)
    inlines = [StudentInline]

    def save_form(self, request, form, change):
        data = super().save_form(request, form, change)
        data.set_password(data.password)
        return data

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


class StudentRoomInline(admin.TabularInline):
    model = RoomAssignments
    fk_name = 'student'
    extra = 1


class MyStudentAdmin(admin.ModelAdmin):
    list_display = ("student_code", "phone_number", "university")
    list_filter = ("university",)
    search_fields = ("university", "phone_number")
    ordering = ("-id",)
    inlines = [StudentRoomInline]


###
class InvoiceItemInline(admin.StackedInline):
    model = InvoiceItems
    extra = 1


class MyInvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "total_amount", "status")
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
    list_display = ("room_number", "room_type", "floor", "total_beds", "building", "active")
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
    list_display = ("id", "student_name", "room", "description", "status")
    list_filter = ("room_id", "status")
    search_fields = ("room__room_number", "description")
    inlines = [ComplaintResponseInline]

    def student_name(self, obj):
        return obj.student.student_code


###
class SurveyQuestionInline(admin.StackedInline):
    model = SurveyQuestion
    extra = 1


class MySurveyAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "user", "created_date", "update_date", "active")
    list_filter = ("active",)
    search_fields = ("title", "description")
    ordering = ("-created_date",)
    inlines = [SurveyQuestionInline]


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
admin_site.register(RoomAssignments)
admin_site.register(Notification)
