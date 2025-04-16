from rest_framework import pagination

class ComplaintsPaginator(pagination.PageNumberPagination):
    page_size = 5