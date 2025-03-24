from rest_framework import pagination

class CoursePaginater(pagination.PageNumberPagination):
    page_size = 1