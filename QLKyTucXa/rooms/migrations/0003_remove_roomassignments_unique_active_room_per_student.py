# Generated by Django 5.1.7 on 2025-06-06 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_remove_roomassignments_unique_student_room_date_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='roomassignments',
            name='unique_active_room_per_student',
        ),
    ]
