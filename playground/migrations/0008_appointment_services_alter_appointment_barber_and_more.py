# Generated by Django 5.0.3 on 2024-08-01 15:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playground', '0007_remove_appointment_services_alter_appointment_barber_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='services',
            field=models.ManyToManyField(through='playground.AppointmentService', to='playground.service'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='barber',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='barber_appointments', to='playground.barber'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='appointment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_appointments', to=settings.AUTH_USER_MODEL),
        ),
    ]
