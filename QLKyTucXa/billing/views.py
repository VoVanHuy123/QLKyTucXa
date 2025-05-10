from datetime import datetime, timedelta

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, generics, permissions, status
from billing.models import Invoice, InvoiceStatus
from billing.serializers import InvoiceSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filter import InvoicesFilter
from .paginators import InvoicePaginater
from .perms import IsAdminOrUserInvoices
from KyTucXa.perms import IsAdminOrUserRoomOwnerReadOnly
from rooms.models import RoomAssignments
from django.conf import settings
from .vnpay import vnpay


class InvoiceViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView,
                     generics.ListAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Invoice.objects.filter(active=True).order_by('-id')
    serializer_class = InvoiceSerializer
    pagination_class = InvoicePaginater
    filter_backends = [DjangoFilterBackend]
    filterset_class = InvoicesFilter
    permission_classes = [IsAdminOrUserRoomOwnerReadOnly]

    @action(detail=False, methods=['get'], url_path='my-room-invoices')
    def my_room_invoices(self, request):
        user = request.user

        if not hasattr(user, 'student') or request.user.student is None:
            return Response({"error": "Tài khoản không liên kết với sinh viên."},
                            status=status.HTTP_400_BAD_REQUEST)

        assignment = RoomAssignments.objects.get(student=user.student, active=True)
        invoices = self.queryset.filter(room=assignment.room)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(invoices, request)

        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='vnpay_payment_url')
    def vnpay_payment_url(self, request, pk=None):
        invoice = self.get_object()
        order_id = invoice.id
        amount = int(invoice.total_amount)
        order_desc = f'Thanh toan hoa don {order_id}'
        client_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

        vnp = vnpay()
        vnp.requestData = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': settings.VNPAY_TMN_CODE,
            'vnp_Amount': amount * 100,
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': order_id,
            'vnp_OrderInfo': order_desc,
            'vnp_OrderType': 'billpayment',
            'vnp_Locale': 'vn',
            'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
            'vnp_IpAddr': client_ip,
            'vnp_ReturnUrl': settings.VNPAY_RETURN_URL
        }

        expire_time = datetime.now() + timedelta(minutes=15)
        vnp.requestData['vnp_ExpireDate'] = expire_time.strftime('%Y%m%d%H%M%S')

        payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
        print(payment_url)
        return Response({'payment_url': payment_url})

    @action(detail=False, methods=['get'], url_path='vnpay_payment_return')
    def payment_return(self, request):
        input_data = request.GET
        vnp = vnpay()
        vnp.responseData = input_data.dict()

        if not vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            return Response({'status': 'error', 'message': 'Invalid checksum'}, status=400)

        txn_ref = input_data.get('vnp_TxnRef')
        response_code = input_data.get('vnp_ResponseCode')

        if response_code == '00':
            invoice = Invoice.objects.get(pk=txn_ref)
            invoice.status = InvoiceStatus.PAID
            invoice.save()

            return Response({'status': 'success', 'message': 'Thanh toán thành công', 'order_id': txn_ref})
        elif response_code == '24':
            return Response({'status': 'canceled', 'message': 'Hủy thanh toán', 'order_id': txn_ref})
        else:
            return Response({'status': 'failed', 'message': 'Thanh toán thất bại', 'order_id': txn_ref})
