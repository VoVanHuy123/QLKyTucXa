# from django.contrib import admin
from django.urls import path, include
from . import views
# from courses.admin import admin_site
from rest_framework.routers import DefaultRouter
from rooms.views import RoomViewSet

routes = DefaultRouter()
routes.register('users', views.UserViewSet, basename='user')
routes.register('rooms',RoomViewSet,basename='room')

urlpatterns = [
    path('', include(routes.urls)),

]