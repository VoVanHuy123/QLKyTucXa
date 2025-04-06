# from django.contrib import admin
from django.urls import path, include
from . import views
# from courses.admin import admin_site
from rest_framework.routers import DefaultRouter
from rooms.views import RoomViewSet, BuidingViewSet
from rooms.views import RoomChangeRequestViewSet
from account.views import UserViewSet

routes = DefaultRouter()
routes.register('users', UserViewSet, basename='user')
routes.register('rooms', RoomViewSet, basename='room')
routes.register('room-change-requset', RoomChangeRequestViewSet, basename="room-change-request")
routes.register('buildings', BuidingViewSet, basename='building')

urlpatterns = [
    path('', include(routes.urls)),

]
