from django.contrib import admin
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path

from .models import Student, Room
from django.utils.html import mark_safe
from django import forms


# Register your models here.
admin_site = admin
admin.site.register(Room)