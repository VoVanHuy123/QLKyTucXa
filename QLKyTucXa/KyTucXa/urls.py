# from django.contrib import admin
from django.urls import path, include
from . import views
# from courses.admin import admin_site
from rest_framework.routers import DefaultRouter
from .update_code import update_code_and_deploy

routes = DefaultRouter()
routes.register('rooms', views.RoomViewSet, basename='room')

urlpatterns = [
    path('', include(routes.urls)),
    path("update-code/", update_code_and_deploy, name="update_code"),

]