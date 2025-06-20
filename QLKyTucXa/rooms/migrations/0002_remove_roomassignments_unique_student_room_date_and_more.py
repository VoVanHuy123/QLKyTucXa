# Generated by Django 5.1.7 on 2025-06-06 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='roomassignments',
            name='unique_student_room_date',
        ),
        migrations.AddConstraint(
            model_name='roomassignments',
            constraint=models.UniqueConstraint(condition=models.Q(('active', True)), fields=('student',), name='unique_active_room_per_student'),
        ),
    ]
