from django.conf import settings
from rest_framework.exceptions import ValidationError
from rooms import perms, serializers, paginators
from rooms.models import Room, Building, RoomChangeRequests, RoomAssignments
from billing.models import Invoice
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from billing.serializers import InvoiceSerializer
from KyTucXa import perms
from django_filters.rest_framework import DjangoFilterBackend
from .filter import RoomFilter, RoomChangeRequestFilter, RoomAssignmentFilter
from billing.paginators import InvoicePaginater
from account.models import Student
import requests


class RoomViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.RetrieveAPIView,
                  generics.UpdateAPIView):
    queryset = Room.objects.filter(active=True).order_by('room_number')
    serializer_class = serializers.RoomSerializer
    permission_classes = [perms.IsAdminOrReadOnly]
    pagination_class = paginators.RoomsPaginater
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomFilter

    @action(detail=False, methods=['get'], url_path='invoices', permission_classes=[perms.IsAdminUser])
    def get_invoices(self, request):
        invoices = Invoice.objects.all()
        return Response(InvoiceSerializer(invoices, many=True).data)

    @action(methods=['get'], detail=True, url_path='invoices', serializer_class=InvoiceSerializer,
            permission_classes=[permissions.IsAuthenticated])
    def get_room_invoices(self, request, pk):
        invoice_id = request.query_params.get('invoice_id', None)
        if invoice_id:
            try:
                invoice = Invoice.objects.get(id=invoice_id, room_id=pk)
                return Response(InvoiceSerializer(invoice).data, status=status.HTTP_200_OK)
            except Invoice.DoesNotExist:
                return Response({"error": "Invoice not found for this room"}, status=status.HTTP_404_NOT_FOUND)
        else:
            invoices = Invoice.objects.filter(room_id=pk)
            paginator = InvoicePaginater()
            page = paginator.paginate_queryset(invoices, request)
            if page is not None:
                serializer = InvoiceSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            return Response(InvoiceSerializer(invoices, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='register-member', permission_classes=[permissions.IsAdminUser])
    def register_member(self, request, pk):
        try:
            room = Room.objects.get(pk=pk, active=True)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        if room.available_beds <= 0:
            return Response({"error": "Phòng đã đầy"}, status=status.HTTP_400_BAD_REQUEST)

        student_id = request.data.get("student_id")
        bed_number = request.data.get("bed_number")

        if not student_id or bed_number is None:
            return Response({"error": "Thiếu thông tin sinh viên hoặc số giường"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Sinh viên không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        if RoomAssignments.objects.filter(room=room, bed_number=bed_number, active=True).exists():
            return Response({"error": f"Giường số {bed_number} đã có người đăng ký"},
                            status=status.HTTP_400_BAD_REQUEST)

        if RoomAssignments.objects.filter(student=student, active=True).exists():
            return Response({"error": "Sinh viên đã ở một phòng khác!"}, status=400)

        assignment = RoomAssignments.objects.create(
            room=room,
            student=student,
            bed_number=bed_number,
            active=True
        )

        room.available_beds -= 1
        if room.available_beds == 0:
            room.status = 'Full'
        room.save()

        return Response(serializers.RoomAssignmentsSerializer(assignment).data, status=status.HTTP_201_CREATED)

    @action(methods=['patch'], detail=True, url_path='remove-member', permission_classes=[permissions.IsAdminUser])
    def remove_member(self, request, pk):
        try:
            room = Room.objects.get(pk=pk, active=True)
        except Room.DoesNotExist:
            return Response({"error": "Phòng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        student_id = request.data.get("student_id")

        if not student_id:
            return Response({"error": "Thiếu thông tin sinh viên"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assignment = RoomAssignments.objects.get(room=room, student_id=student_id, active=True)
        except RoomAssignments.DoesNotExist:
            return Response({"error": "Sinh viên không ở phòng này hoặc đã bị xóa"}, status=status.HTTP_404_NOT_FOUND)

        assignment.active = False
        assignment.save()

        room.available_beds += 1
        if room.status == 'Full':
            room.status = 'Empty'
        room.save()

        return Response({"message": "Xóa thành viên khỏi phòng thành công!"}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='room-assignments',
            serializer_class=serializers.RoomAssignmentsSerializer, permission_classes=[permissions.IsAuthenticated])
    def room_assignments(self, request, pk=None):

        try:
            room = Room.objects.get(pk=pk, active=True)
        except Room.DoesNotExist:
            return Response({"error": "Phòng không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

        assignments = RoomAssignments.objects.filter(room=room, active=True)

        serializer = serializers.RoomAssignmentsSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='my-room', permission_classes=[perms.IsStudentUser])
    def my_room(self, request):
        user = request.user

        try:
            assignment = RoomAssignments.objects.get(student=user.student, active=True)
        except RoomAssignments.DoesNotExist:
            return Response({"error": "Sinh viên chưa có phòng."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(assignment.room)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BuidingViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.ListAPIView):
    queryset = Building.objects.filter(active=True).order_by("building_name")
    serializer_class = serializers.BuildingSerializer
    permission_classes = [perms.IsAdminOrReadOnly]


class RoomChangeRequestViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView, generics.ListAPIView,
                               generics.UpdateAPIView):
    queryset = RoomChangeRequests.objects.filter(active=True)
    serializer_class = serializers.RoomChangeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = paginators.RoomChangeRequestsPaginater

    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomChangeRequestFilter

    def get_permissions(self):
        if self.action in ['create', 'room_change_request']:
            return [perms.IsStudentUser()]
        elif self.action in ['list', 'update', 'partial_update', 'destroy']:
            return [perms.IsAdminUser()]
        elif self.action in ['retrieve']:
            return [perms.IsAdminOrUserObjectOwner()]
        return [perms.IsAuthenticatedUser()]

    def perform_create(self, serializer):
        user = self.request.user

        try:
            assignment = RoomAssignments.objects.get(student=user.student, active=True)
        except RoomAssignments.DoesNotExist:
            raise ValidationError({"error": "Sinh viên chưa có phòng."})

        serializer.save(student=user.student, current_room=assignment.room)

    @action(methods=['get'], detail=False, url_path='my-room-change-requests')
    def room_change_request(self, request):
        user = request.user

        change_requests = self.queryset.filter(student=user.student).order_by('-id')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(change_requests, request)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(change_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoomAssignmentsViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = RoomAssignments.objects.filter(active=True)
    serializer_class = serializers.RoomAssignmentsSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RoomAssignmentFilter


class MapViewSet(viewsets.ViewSet):
    permission_classes = [perms.IsAuthenticatedUser]

    @staticmethod
    def decode_polyline(polyline_str):
        points = []
        index = 0
        length = len(polyline_str)
        lat = 0
        lng = 0

        while index < length:
            shift = 0
            result = 0
            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if byte < 0x20:
                    break
            delta_lat = ~(result >> 1) if result & 1 else result >> 1
            lat += delta_lat

            shift = 0
            result = 0
            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if byte < 0x20:
                    break
            delta_lng = ~(result >> 1) if result & 1 else result >> 1
            lng += delta_lng

            points.append({'latitude': lat / 1e5, 'longitude': lng / 1e5})

        return points

    @action(methods=['get'], detail=False, url_path='get-direction')
    def map(self, request):
        origin_lat = request.query_params.get('origin_lat')
        origin_lng = request.query_params.get('origin_lng')
        dest_lat = request.query_params.get('dest_lat')
        dest_lng = request.query_params.get('dest_lng')

        if not all([origin_lat, origin_lng, dest_lat, dest_lng]):
            raise ValidationError(
                {"error": "Missing parameters, please provide origin_lat, origin_lng, dest_lat, dest_lng"})

        try:
            origin_lat = float(origin_lat)
            origin_lng = float(origin_lng)
            dest_lat = float(dest_lat)
            dest_lng = float(dest_lng)
        except ValueError:
            raise ValidationError({"error": "Invalid coordinates, please provide valid float values for lat/lng."})

        google_maps_api_key = settings.GOOGLE_MAPS_APIKEY
        url = f'https://maps.googleapis.com/maps/api/directions/json'
        params = {
            'origin': f'{origin_lat},{origin_lng}',
            'destination': f'{dest_lat},{dest_lng}',
            'key': google_maps_api_key,
            'mode': 'driving'
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data['status'] == 'OK' and data['routes']:
                polyline_str = data['routes'][0].get('overview_polyline', {}).get('points', '')
                route_points = self.decode_polyline(polyline_str)

                route_data = {
                    'legs': data['routes'][0].get('legs', []),
                    'overview_polyline': route_points
                }
                return Response(route_data)
            else:
                return Response({"error": "No route found or Google Maps API error."}, status=400)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Error while fetching route from Google Maps API", "details": str(e)}, status=500)
