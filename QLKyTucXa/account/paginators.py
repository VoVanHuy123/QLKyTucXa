from rest_framework import pagination

class StudentPaginater(pagination.PageNumberPagination):
    page_size = 10