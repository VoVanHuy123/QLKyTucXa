# Generated by Django 5.1.7 on 2025-03-25 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KyTucXa', '0002_complaintsresponse'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='description',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
