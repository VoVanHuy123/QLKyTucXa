# Generated by Django 5.1.7 on 2025-04-09 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid')], default='Unpaid', max_length=20),
        ),
    ]
