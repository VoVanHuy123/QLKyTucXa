from symtable import Class

from django.contrib import admin
from rooms.models import Room, Building, RoomChangeRequests, RoomAssignments
from billing.models import Invoice, InvoiceItems
from account.models import User, Student
from support.models import Complaints, ComplaintsResponse
from surveys.models import Survey, SurveyResponse, SurveyQuestion


class MyAdminSite(admin.AdminSite):
    site_header = "Quản lý ký túc xá"
    site_title = "Quản lý ký túc xá"
    index_title = "Chào mừng đến với trang quản trị"


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
