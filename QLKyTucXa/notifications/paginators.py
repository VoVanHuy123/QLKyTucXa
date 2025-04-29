from rest_framework import pagination

class NotiPaginater(pagination.PageNumberPagination):
    page_size = 6