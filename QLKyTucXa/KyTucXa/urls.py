# from django.contrib import admin
from django.urls import path, include
from . import views
# from courses.admin import admin_site
from rest_framework.routers import DefaultRouter
from rooms.views import RoomViewSet, BuidingViewSet,RoomChangeRequestViewSet,RoomAssignmentsViewSet
from account.views import UserViewSet
from billing.views import InvoiceViewSet
from support.views import ComplaintsViewSet, ComplaintsResponseViewSet
from surveys.views import SurveyViewSet, SurveyQuestionViewSet, StatisticsViewSet
from notifications.views import NotiViewSet

routers = DefaultRouter()
routers.register('users', UserViewSet, basename='user')
routers.register('rooms', RoomViewSet, basename='room')
routers.register('room-change-requests', RoomChangeRequestViewSet, basename="room-change-requests")
routers.register('buildings', BuidingViewSet, basename='building')
routers.register('invoices', InvoiceViewSet, basename='invoices')
routers.register('complaints', ComplaintsViewSet, basename='complaints')
routers.register('complaints-responses', ComplaintsResponseViewSet, basename='complaints-responses')
routers.register('room-assignments', RoomAssignmentsViewSet, basename='room-assignments')
routers.register('surveys', SurveyViewSet, basename='surveys')
routers.register('survey-questions', SurveyQuestionViewSet, basename='survey-questions')
routers.register('notifications', NotiViewSet, basename='notifications')
routers.register('statistics', StatisticsViewSet, basename='statistics')


urlpatterns = [
    path('', include(routers.urls)),

]
