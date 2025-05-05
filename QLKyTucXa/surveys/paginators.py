from rest_framework import pagination

class SurveyPaginator(pagination.PageNumberPagination):
    page_size = 10