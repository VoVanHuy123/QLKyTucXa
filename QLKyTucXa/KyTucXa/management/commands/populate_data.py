from datetime import date

from django.core.management.base import BaseCommand
from faker import Faker
import random
from account.models import User, Student
from rooms.models import Building, Room, RoomAssignments, RoomStatus
from billing.models import Invoice, InvoiceItems
from support.models import Complaints, ComplaintsResponse
from surveys.models import Survey, SurveyQuestion, SurveyResponse


class Command(BaseCommand):
    help = 'Populate the database with sample data for all models'

    def handle(self, *args, **kwargs):
        fake = Faker('vi_VN')
        Faker.seed(0)

        # Clear old data
        RoomAssignments.objects.all().delete()
        User.objects.all().delete()
        Student.objects.all().delete()
        Building.objects.all().delete()
        Room.objects.all().delete()
        Invoice.objects.all().delete()
        InvoiceItems.objects.all().delete()
        Complaints.objects.all().delete()
        ComplaintsResponse.objects.all().delete()
        Survey.objects.all().delete()
        SurveyQuestion.objects.all().delete()
        SurveyResponse.objects.all().delete()

        self.stdout.write("Deleted old data from all tables.")

        # Create Admin
        admin_user = User.objects.create(
            username="admin1",
            email="admin1@gmail.com",
            role='Admin',
            is_staff=1
        )
        admin_user.set_password('123456')
        admin_user.save()
        self.stdout.write(f'Created Admin User: {admin_user.username}')

        # Populate Students
        students = []
        for _ in range(10):
            full_name = fake.name()
            student = Student.objects.create(
                username=f"sv{fake.unique.random_int(100, 999)}",
                email=fake.unique.email(),
                role='Student',
                student_code=fake.unique.random_int(min=1000000000, max=9999999999),
                university="Đại học Mở TP.HCM",
            )
            student.set_password('123456')
            student.save()
            students.append(student)
            self.stdout.write(f'Created Student: {student.username}')

        # Populate Buildings
        building_codes = ['A', 'B', 'C', 'D', 'E']
        buildings = []
        for code in building_codes:
            building = Building.objects.create(
                building_name=f"{code}",
                total_floors=random.randint(3, 5),
            )
            buildings.append(building)
            self.stdout.write(f'Created Building: {building.building_name}')

        # Populate Rooms
        rooms = []
        for building in buildings:
            for floor in range(1, building.total_floors + 1):
                for i in range(1, 4):
                    room_number = f"{building.building_name}{floor}0{i}"
                    room = Room.objects.create(
                        building=building,
                        room_number=room_number,
                        room_type=random.choice(["Standard"]),
                        floor=floor,
                        total_beds=6,
                        available_beds=6,
                        monthly_fee=1000000,
                    )
                    rooms.append(room)
                    self.stdout.write(f'Created Room: {room.room_number} - {room.room_type}')

        # Populate Room Assignments
        for student in students:
            room = next((r for r in rooms if r.available_beds > 0), None)
            if room:
                assigned_beds = RoomAssignments.objects.filter(room=room).values_list('bed_number', flat=True)
                free_beds = list(set(range(1, room.total_beds + 1)) - set(assigned_beds))
                if free_beds:
                    bed_number = random.choice(free_beds)
                    RoomAssignments.objects.create(
                        student=student,
                        room=room,
                        bed_number=bed_number,
                    )
                    room.available_beds -= 1
                    if room.available_beds == 0:
                        room.status = RoomStatus.FULL
                    room.save()
                    self.stdout.write(f'Assigned {student.username} to Room {room.room_number}, Bed {bed_number}')

        # Populate Invoices
        for room in rooms:
            invoice = Invoice.objects.create(
                description="Hóa đơn tháng 5",
                room=room,
                total_amount=1300000,
                status='Unpaid',
                invoice_month=date(date.today().year, 5, 1)
            )
            self.stdout.write(f'Created Invoice for Room {room.room_number}')

            for desc in ["Tiền điện", "Tiền nước", "Phí vệ sinh"]:
                item = InvoiceItems.objects.create(
                    invoice=invoice,
                    description=desc,
                    amount=100000,
                )
                self.stdout.write(f' - Item: {desc}')

        # Populate Complaints
        issues = ["Máy lạnh hư", "Đèn bị chập", "Nước yếu", "Bạn cùng phòng ồn ào"]
        for student in students:
            for _ in range(2):
                room = random.choice(rooms)
                complaint = Complaints.objects.create(
                    student=student,
                    room=room,
                    title=random.choice(issues),
                    description=fake.text(),
                    status='Pending',
                )
                self.stdout.write(f'Created Complaint: {complaint.title}')

        # Populate Surveys
        questions_bank = [
            "Bạn hài lòng với cơ sở vật chất không?",
            "Thái độ nhân viên ký túc xá như thế nào?",
            "Bạn có đề xuất gì để cải thiện dịch vụ?"
        ]
        for i in range(3):
            survey = Survey.objects.create(
                title=f"Khảo sát chất lượng KTX lần {i+1}",
                description=fake.text(),
                user=admin_user,
            )
            self.stdout.write(f'Created Survey: {survey.title}')

            for q in questions_bank:
                question = SurveyQuestion.objects.create(
                    survey=survey,
                    question_text=q,
                    question_type='Text',
                )
                for student in students:
                    SurveyResponse.objects.create(
                        survey=survey,
                        question=question,
                        student=student,
                        answer=fake.sentence(),
                    )
            self.stdout.write(f'Added {len(questions_bank)} questions and responses to {survey.title}')
