from django.shortcuts import render
from rest_framework import viewsets, generics, status,parsers,permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from KyTucXa.models import Room,User
from KyTucXa import serializers,paginators,perms

# Create your views here.

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    @action(methods=['get','patch'],url_path="current-user",detail=False, permission_classes = [permissions.IsAuthenticated])
    def get_curent_user(self,request):

        if request.method.__eq__("PATCH"):
            u = request.user
            for key in request.data:
                if key in ['first_name','last_name']:
                    setattr(u,key,request.data[key])

                elif key.__eq__('password'):
                    u.set_password(request.data[key])
            u.save()
            return Response(serializers.UserSerializer(u).data)
        else:
            return Response(serializers.UserSerializer(request.user).data)

#bung hết api của Room
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(status='Empty')
    serializer_class = serializers.RoomSerializer
    permission_classes = [perms.IsAdminOrReadOnly]
    
