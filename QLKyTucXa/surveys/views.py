from django.db.models import Q
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action

from .models import Survey, SurveyResponse, SurveyQuestion
from . import models, paginators, serializers
from KyTucXa.perms import IsAdminUser, IsAuthenticatedUser, IsAdminOrReadOnly, IsObjectOwner, IsStudentOrAdminReadOnly
from rest_framework.response import Response


class SurveyViewSet(viewsets.ViewSet, generics.ListAPIView, generics.DestroyAPIView):
    queryset = Survey.objects.filter(active=True).order_by('-id')
    pagination_class = paginators.SurveyPaginator
    serializer_class = serializers.SurveySerializer
    permission_classes = [IsAdminOrReadOnly, IsObjectOwner]

    def get_queryset(self):
        queryset = self.queryset

        submitted_ids = SurveyResponse.objects.filter(student=self.request.user).values_list('survey_id', flat=True)
        queryset = queryset.exclude(id__in=submitted_ids)

        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))

        return queryset

    def create(self, request):
        data = request.data.copy()
        data['user'] = request.user.id

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            survey = Survey.objects.get(pk=pk, active=True)
        except Survey.DoesNotExist:
            return Response({"error": "Không tìm thấy."}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, survey)

        data = request.data.copy()
        data['user'] = request.user.id

        serializer = self.serializer_class(survey, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'], url_path='survey-questions')
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
        else:
            try:
                survey = self.queryset.get(pk=pk)
            except Survey.DoesNotExist:
                return Response({"error": "Không tìm thấy."}, status=status.HTTP_404_NOT_FOUND)
            questions = survey.questions.filter(active=True)

            paginator = self.pagination_class()
            # page = paginator.paginate_queryset(questions, request)

            # if page is not None:
            #     serializer = serializers.SurveyQuestionSerializer(page, many=True)
            #     return paginator.get_paginated_response(serializer.data)

            serializer = serializers.SurveyQuestionSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'], url_path='survey-responses',
            permission_classes=[IsStudentOrAdminReadOnly])
    def create_responses(self, request, pk):
        if request.method == 'POST':
            try:
                survey = self.queryset.get(pk=pk)
            except Survey.DoesNotExist:
                return Response({"error": "Không tìm thấy."}, status=status.HTTP_404_NOT_FOUND)

            responses_data = request.data.copy()

            if not responses_data:
                return Response({"error": "Không có dữ liệu được cung cấp."}, status=status.HTTP_400_BAD_REQUEST)

            survey_responses = []
            for response in responses_data:
                response['survey'] = pk
                response['student'] = request.user.id
                response_serializer = serializers.SurveyResponseSerializer(data=response)

                if response_serializer.is_valid():
                    survey_responses.append(response_serializer.save())
                else:
                    return Response(response_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializers.SurveyResponseSerializer(survey_responses, many=True).data,
                            status=status.HTTP_201_CREATED)
        else:
            try:
                survey = self.queryset.get(pk=pk)
            except Survey.DoesNotExist:
                return Response({"error": "Không tìm thấy."}, status=status.HTTP_404_NOT_FOUND)

            responses = survey.responses.filter(active=True)

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(responses, request)

            if page is not None:
                serializer = serializers.SurveyResponseSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = serializers.SurveyResponseSerializer(responses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='survey-history', permission_classes=[IsAuthenticatedUser])
    def get_surveys_history(self, request):
        queryset = Survey.objects.filter(active=True).order_by('-id')
        submitted_ids = SurveyResponse.objects.filter(student=request.user.student).values_list('survey_id', flat=True)
        surveys = queryset.filter(id__in=submitted_ids)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(surveys, request)

        if page is not None:
            serializer = serializers.SurveySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = serializers.SurveySerializer(surveys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SurveyQuestionViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = SurveyQuestion.objects.filter(active=True).order_by('-id')
    pagination_class = paginators.SurveyPaginator
    serializer_class = serializers.SurveyQuestionSerializer
    permission_classes = [IsAuthenticatedUser]
