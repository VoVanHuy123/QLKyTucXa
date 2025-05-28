from rest_framework import pagination

class RoomsPaginater(pagination.PageNumberPagination):
    page_size = 6

class RoomChangeRequestsPaginater(pagination.PageNumberPagination):
    page_size = 8