from rest_framework import viewsets, generics, status, mixins, permissions, parsers
from rest_framework.decorators import action
from . import models, paginators, serializers
from .models import Complaints, ComplaintsStatus, ComplaintsResponse, ComplaintsStatus
from KyTucXa.perms import IsAuthenticatedUser, IsStudentUser, IsAdminOrUserRoomOwnerReadOnly, IsAdminUser
from rest_framework.response import Response
from rooms.models import RoomAssignments
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend


class ComplaintsViewSet(viewsets.ViewSet):
    queryset = Complaints.objects.filter(active=True).order_by('-id')
    pagination_class = paginators.ComplaintsPaginator
    serializer_class = serializers.ComplaintsSerializer
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def get_permissions(self):
        if self.action in ['create']:
            return [IsStudentUser()]
        elif self.action in ['retrieve', 'complaints_responses']:
            return [IsAdminOrUserRoomOwnerReadOnly()]
        elif self.action in ['list', 'resolve']:
            return [IsAdminUser()]
        return [IsAuthenticatedUser()]

    def get_queryset(self):
        queryset = self.queryset

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(status__exact=q))

        return queryset

    def create(self, request):
        user = request.user
        data = request.data.copy()

        try:
            assignment = RoomAssignments.objects.get(student=user.student, active=True)
        except RoomAssignments.DoesNotExist:
            return Response({"error": "Sinh viên chưa có phòng."}, status=status.HTTP_400_BAD_REQUEST)
        data["room"] = assignment.room.id
        data["student"] = user.student.id
        data['active'] = True
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk):
        try:
            complaint = self.queryset.get(pk=pk)
            self.check_object_permissions(request, complaint)
        except Complaints.DoesNotExist:
            return Response({"error": "Không tìm thấy."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(complaint)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        complaints = self.get_queryset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(complaints, request)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='my-room-complaints')
    def my_room_complaints(self, request):
        user = request.user

        if not hasattr(user, 'student') or request.user.student is None:
            return Response({"error": "Tài khoản không liên kết với sinh viên."},
                            status=status.HTTP_400_BAD_REQUEST)

        assignment = RoomAssignments.objects.get(student=user.student, active=True)
        complaints = self.get_queryset().filter(room=assignment.room)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(complaints, request)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='my-complaints')
    def my_complaints(self, request):
        user = request.user

        if not hasattr(user, 'student') or request.user.student is None:
            return Response({"error": "Tài khoản không liên kết với sinh viên."},
                            status=status.HTTP_400_BAD_REQUEST)

        assignment = RoomAssignments.objects.get(student=user.student, active=True)
        complaints = self.get_queryset().filter(room=assignment.room, student=user.student).order_by('-id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(complaints, request)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'], url_path='complaints-responses')
    def complaints_responses(self, request, pk):
        if request.method == 'POST':
            try:
                complaint = self.queryset.get(pk=pk)
                complaint.status = ComplaintsStatus.RESOLVED
                complaint.save()

                data = request.data.copy()
                data["user"] = request.user.id
                data["complaint"] = pk
                serializer = serializers.ComplaintsResponseSerializer(data=data)

                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Complaints.DoesNotExist:
                return Response({"error": "Không tìm thấy."}, status=status.HTTP_404_NOT_FOUND)

        else:
            try:
                complaint = self.queryset.get(pk=pk)
                self.check_object_permissions(request, complaint)
            except Complaints.DoesNotExist:
                return Response({"error": "Không tìm thấy."}, status=status.HTTP_404_NOT_FOUND)
            responses = complaint.responses.filter(active=True).order_by('-id')

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(responses, request)

            if page is not None:
                serializer = serializers.ComplaintsResponseSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = serializers.ComplaintsResponseSerializer(responses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='resolve')
    def resolve_complaint(self, request, pk):
        try:
            complaint = self.queryset.get(pk=pk)
            self.check_object_permissions(request, complaint)
        except Complaints.DoesNotExist:
            return Response({"error": "Không tìm thấy khiếu nại."}, status=status.HTTP_404_NOT_FOUND)

        complaint.status = ComplaintsStatus.RESOLVED
        complaint.save()

        serializer = self.serializer_class(complaint)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ComplaintsResponseViewSet(viewsets.ViewSet):
    queryset = ComplaintsResponse.objects.filter(active=True)
    models = ComplaintsResponse
    pagination_class = paginators.ComplaintsPaginator
    serializer_class = serializers.ComplaintsResponseSerializer

    def get_permissions(self):
        if self.action in ['retrieve']:
            return [IsAdminOrUserRoomOwnerReadOnly()]
        return [IsAuthenticatedUser()]

    def retrieve(self, request, pk):
        try:
            response = self.queryset.get(pk=pk)
            complaint = response.complaint
            self.check_object_permissions(request, complaint)
        except ComplaintsResponse.DoesNotExist:
            return Response({"error": "Không tìm thấy."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(response)
        return Response(serializer.data, status=status.HTTP_200_OK)
