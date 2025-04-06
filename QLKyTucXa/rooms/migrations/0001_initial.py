# Generated by Django 5.1.7 on 2025-04-05 16:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('building_name', models.CharField(max_length=50)),
                ('total_floors', models.IntegerField()),
            ],
            options={
                'db_table': 'building',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('room_number', models.CharField(max_length=10, unique=True)),
                ('room_type', models.CharField(max_length=50, null=True)),
                ('floor', models.IntegerField(null=True)),
                ('total_beds', models.IntegerField()),
                ('available_beds', models.IntegerField()),
                ('status', models.CharField(choices=[('Empty', 'Empty'), ('Full', 'Full')], default='Empty', max_length=20)),
                ('monthly_fee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rooms.building')),
            ],
            options={
                'db_table': 'room',
            },
        ),
        migrations.CreateModel(
            name='RoomAssignments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('bed_number', models.IntegerField()),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rooms.room')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='account.student')),
            ],
            options={
                'db_table': 'room_assignments',
            },
        ),
        migrations.CreateModel(
            name='RoomChangeRequests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('reason', models.CharField(max_length=500)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=50)),
                ('current_room', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='current_room', to='rooms.room')),
                ('requested_room', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='requested_room', to='rooms.room')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='account.student')),
            ],
            options={
                'db_table': 'room_change_requests',
            },
        ),
    ]
