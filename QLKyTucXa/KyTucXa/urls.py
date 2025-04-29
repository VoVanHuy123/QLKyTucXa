# from django.contrib import admin
from django.urls import path, include
from . import views
# from courses.admin import admin_site
from rest_framework.routers import DefaultRouter
from rooms.views import RoomViewSet, BuidingViewSet,RoomChangeRequestViewSet,RoomAssignmentsViewSet
from account.views import UserViewSet
from billing.views import InvoiceViewSet
from support.views import ComplaintsViewSet, ComplaintsResponseViewSet
from surveys.views import SurveyViewSet, SurveyQuestionViewSet
from notifications.views import NotiViewSet

routes = DefaultRouter()
routes.register('users', UserViewSet, basename='user')
routes.register('rooms', RoomViewSet, basename='room')
routes.register('room-change-requests', RoomChangeRequestViewSet, basename="room-change-requests")
routes.register('buildings', BuidingViewSet, basename='building')
routes.register('invoices', InvoiceViewSet, basename='invoices')
routes.register('complaints', ComplaintsViewSet, basename='complaints')
routes.register('complaints-responses', ComplaintsResponseViewSet, basename='complaints-responses')
routes.register('room-assignments', RoomAssignmentsViewSet, basename='room-assignments')
routes.register('surveys', SurveyViewSet, basename='surveys')
routes.register('survey-questions', SurveyQuestionViewSet, basename='survey-questions')
routes.register('notifications', NotiViewSet, basename='notifications')

urlpatterns = [
    path('', include(routes.urls)),

]
