from rest_framework import pagination

class SurveyPaginater(pagination.PageNumberPagination):
    page_size = 5