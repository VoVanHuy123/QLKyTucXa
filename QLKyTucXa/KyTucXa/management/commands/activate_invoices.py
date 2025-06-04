import logging
from django.core.management.base import BaseCommand
from datetime import date, timedelta

from account.models import User
from billing.models import Invoice
from config.PushNoti import send_push_notification

logging.basicConfig(
    filename='D:/dev/CCNLTHD/logs/invoice_log.txt',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    encoding='utf-8'
)


# logging.basicConfig(
#     filename='/home/yuh1117/logs/invoice_log.txt',
#     level=logging.INFO,
#     format='[%(asctime)s] %(levelname)s - %(message)s',
#     encoding='utf-8'
# )

def is_last_day_of_month(d):
    next_day = d + timedelta(days=1)
    return next_day.day == 1


class Command(BaseCommand):
    help = 'Kích hoạt hóa đơn cuối tháng'

    def handle(self, *args, **kwargs):
        today = date.today()

        if not is_last_day_of_month(today):
            msg = 'Không phải ngày cuối tháng.'
            self.stdout.write(self.style.WARNING(msg))
            logging.warning(msg)
            return

        updated = Invoice.objects.filter(
            invoice_month__year=today.year,
            invoice_month__month=today.month,
            active=False
        ).update(active=True)

        if updated > 0:
            msg = f'Kích hoạt {updated} hóa đơn.'
            self.stdout.write(self.style.SUCCESS(msg))
            logging.info(msg)

            users = User.objects.exclude(expo_token=None).exclude(expo_token="")

            for user in users:
                send_push_notification(
                    user.expo_token,
                    "Thanh toán hóa đơn",
                    f"Hóa tháng {today.month}/{today.year}"
                )
        else:
            msg = 'Không có hóa đơn cần kích hoạt.'
            self.stdout.write(msg)
            logging.info(msg)
