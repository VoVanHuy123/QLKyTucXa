from rest_framework import pagination

class InvoicePaginater(pagination.PageNumberPagination):
    page_size = 10