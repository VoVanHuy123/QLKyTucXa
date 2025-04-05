# from django.contrib import admin
from django.urls import path, include
from . import views
# from courses.admin import admin_site
from rest_framework.routers import DefaultRouter
from rooms.views import RoomViewSet,BuidingViewSet
from support.views import RoomChangeRequestViewSet

routes = DefaultRouter()
routes.register('users', views.UserViewSet, basename='user')
routes.register('rooms',RoomViewSet,basename='room')
routes.register('room-change-requset',RoomChangeRequestViewSet,basename="roomchangerequest")
routes.register('buildings',BuidingViewSet,basename='building')

urlpatterns = [
    path('', include(routes.urls)),

]