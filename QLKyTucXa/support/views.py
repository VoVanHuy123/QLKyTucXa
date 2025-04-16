from rest_framework import viewsets, generics, status, mixins
from . import models, paginators, serializers
from .models import Complaints, ComplaintsStatus, ComplaintsResponse
from KyTucXa.perms import IsAdminOrUserComplaintsOwner, IsAdminUser


class ComplaintsViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = Complaints.objects.filter(active=True)
    pagination_class = paginators.ComplaintsPaginator
    serializer_class = serializers.ComplaintsSerializer

    def get_permissions(self):
        if self.action in ['retrieve']:
            return [IsAdminOrUserComplaintsOwner()]
        else:
            return [IsAdminUser()]
