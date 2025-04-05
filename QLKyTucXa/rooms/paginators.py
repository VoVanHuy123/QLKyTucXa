from rest_framework import pagination

class RoomsPaginater(pagination.PageNumberPagination):
    page_size = 6