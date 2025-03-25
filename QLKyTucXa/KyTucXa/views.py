from django.shortcuts import render , get_object_or_404
from rest_framework import viewsets, generics, status,parsers,permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from KyTucXa.models import Room,User,RoomChangeRequests
from KyTucXa import serializers,paginators,perms
from support.serializers import RoomChangeRequestSerializer

# Create your views here.

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView,generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    #/user/current-user/
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
    #/user/{id}/delete-user/
    @action(methods=['delete'],detail=True,permission_classes = [permissions.IsAdminUser])
    def delete_user(self,request,pk):
        user=get_object_or_404(User,pk=pk)
        if user.is_superuser:
            return Response({"error" : "Không thể xóa tài khoản admin"},status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response({"message":"Xóa người dùng thành công!"},status=status.HTTP_204_NO_CONTENT)
    #/user/{id}/requests/
    @action(methods=['get'],detail=True,url_path="requests")
    def get_invoices(self,request,pk):
        invoices = RoomChangeRequests.objects.filter(user_id = pk)
        return Response(RoomChangeRequestSerializer(invoices,many=True).data)
    


    

