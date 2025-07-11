from django.db.models import Q, Count
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action

from .models import Survey, SurveyResponse, SurveyQuestion
from account.models import Student
from rooms.models import Room, Building
from . import models, paginators, serializers
from KyTucXa.perms import IsAdminUser, IsAuthenticatedUser, IsAdminOrReadOnly, IsObjectOwner, IsStudentOrAdmin
from rest_framework.response import Response


class SurveyViewSet(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView, generics.CreateAPIView):
    queryset = Survey.objects.filter(active=True).order_by('-id')
    pagination_class = paginators.SurveyPaginator
    serializer_class = serializers.SurveySerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_authenticated:
            submitted_ids = SurveyResponse.objects.filter(student=self.request.user).values_list('survey_id', flat=True)
            queryset = queryset.exclude(id__in=submitted_ids)

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))

        return queryset

    @action(detail=True, methods=['get', 'post'], url_path='survey-responses',
            serializer_class=serializers.SurveyResponseSerializer, permission_classes=[IsStudentOrAdmin])
    def create_responses(self, request, pk):
        try:
            survey = self.queryset.get(pk=pk)
        except Survey.DoesNotExist:
            return Response({"error": "Không tìm thấy khảo sát."}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            responses_data = request.data
            if not responses_data:
                return Response({"error": "Không có dữ liệu được cung cấp."}, status=status.HTTP_400_BAD_REQUEST)

            if not hasattr(request.user, 'student') or request.user.student is None:
                return Response({"error": "Tài khoản không liên kết với sinh viên."},
                                status=status.HTTP_400_BAD_REQUEST)

            created_responses = []
            for response in responses_data:
                response['survey'] = survey.id
                response['student'] = request.user.student.id

                serializer = serializers.SurveyResponseSerializer(data=response)
                if serializer.is_valid():
                    serializer.save()
                    created_responses.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(created_responses, status=status.HTTP_201_CREATED)

        else:  # GET
            question_id = request.query_params.get('question')
            student_id = request.query_params.get('student')

            responses = survey.responses.filter(active=True).order_by('id')

            if question_id:
                responses = responses.filter(question_id=question_id)

            if student_id:
                responses = responses.filter(student_id=student_id)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(responses, request)
            serializer = self.serializer_class(page or responses, many=True)
            return paginator.get_paginated_response(serializer.data) if page else Response(serializer.data,
                                                                                           status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='survey-history', permission_classes=[IsAuthenticatedUser])
    def get_surveys_history(self, request):
        queryset = self.queryset
        submitted_ids = SurveyResponse.objects.filter(student=request.user.student).values_list('survey_id', flat=True)
        surveys = queryset.filter(id__in=submitted_ids)

        q = self.request.query_params.get('q')
        if q:
            surveys = surveys.filter(Q(title__icontains=q) | Q(description__icontains=q))

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(surveys, request)

        if page is not None:
            serializer = serializers.SurveySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = serializers.SurveySerializer(surveys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'], url_path='survey-questions',
            serializer_class=serializers.SurveyQuestionSerializer)
    def survey_questions(self, request, pk):
        if request.method == 'POST':
            try:
                survey = self.queryset.get(pk=pk)
                data = request.data.copy()
                if not data:
                    return Response({"error": "Không có dữ liệu được cung cấp."}, status=status.HTTP_400_BAD_REQUEST)

                survey_questions = []
                for question in data:
                    question['survey'] = pk
                    serializer = serializers.SurveyQuestionSerializer(data=question)

                    if serializer.is_valid():
                        survey_questions.append(serializer.save())
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response(serializers.SurveyQuestionSerializer(survey_questions, many=True).data,
                                status=status.HTTP_201_CREATED)
            except Survey.DoesNotExist:
                return Response({"error": "Không tìm thấy."}, status=status.HTTP_404_NOT_FOUND)
        elif request.method == "GET":
            try:
                survey = self.queryset.get(pk=pk)
            except Survey.DoesNotExist:
                return Response({"error": "Không tìm thấy."}, status=status.HTTP_404_NOT_FOUND)
            questions = survey.questions.filter(active=True)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(questions, request)

            if page is not None:
                serializer = serializers.SurveyQuestionSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = serializers.SurveyQuestionSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='survey-student-count', permission_classes=[permissions.IsAdminUser])
    def get_surveys_student_count(self, request, pk=None):
        try:
            survey = self.get_object()

            total_students = Student.objects.filter(is_active=True).distinct().count()
            answered_students = SurveyResponse.objects.filter(survey=survey).values('student').distinct().count()

            return Response({
                'survey_id': survey.id,
                'survey_title': survey.title,
                'answered_students': answered_students,
                'total_students': total_students,
                'answered_percent': round((answered_students / total_students) * 100, 2) if total_students > 0 else 0
            })

        except Survey.DoesNotExist:
            return Response({'error': 'Không tim thấy khảo sát'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class SurveyQuestionViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = SurveyQuestion.objects.filter(active=True).order_by('-id')
    pagination_class = paginators.SurveyPaginator
    serializer_class = serializers.SurveyQuestionSerializer
    permission_classes = [IsAuthenticatedUser]


class StatisticsViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'], url_path='summary', permission_classes=[IsAdminUser])
    def summary(self, request):
        total_students = Student.objects.filter(is_active=True).distinct().count()
        total_rooms = Room.objects.count()
        total_buildings = Building.objects.count()

        data = {
            "total_students": total_students,
            "total_rooms": total_rooms,
            "total_buildings": total_buildings,
        }
        return Response(data)

    @action(detail=False, methods=['get'], url_path='detail', permission_classes=[IsAdminUser])
    def building_detail(self, request):
        building_detail = Building.objects.annotate(
            total_rooms=Count('rooms', distinct=True),
            total_students=Count('rooms__room_assignments', filter=Q(rooms__room_assignments__active=True)),
            room_still_empty=Count('rooms', filter=Q(rooms__status="Empty"), distinct=True)
        ).values('id', 'building_name', 'total_rooms', 'total_students', 'room_still_empty')

        data = {
            "building_detail": building_detail
        }
        return Response(data)
