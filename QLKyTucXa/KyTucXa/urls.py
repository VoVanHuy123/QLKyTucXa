# from django.contrib import admin
from django.urls import path, include
from . import views
# from courses.admin import admin_site
from rest_framework.routers import DefaultRouter
from rooms.views import RoomViewSet, BuidingViewSet,RoomChangeRequestViewSet,RoomAssignmentsViewSet
from account.views import UserViewSet
from billing.views import InvoiceViewSet

routes = DefaultRouter()
routes.register('users', UserViewSet, basename='user')
routes.register('rooms', RoomViewSet, basename='room')
routes.register('room-change-requset', RoomChangeRequestViewSet, basename="room-change-request")
routes.register('buildings', BuidingViewSet, basename='building')
routes.register('invoices', InvoiceViewSet, basename='invoices')
routes.register('room-assignments', RoomAssignmentsViewSet, basename='room-assignments')

urlpatterns = [
    path('', include(routes.urls)),

]
