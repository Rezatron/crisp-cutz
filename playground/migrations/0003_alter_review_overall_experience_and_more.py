# Generated by Django 5.0.3 on 2024-08-17 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playground', '0002_notification_appointment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='overall_experience',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='servicereview',
            name='stars',
            field=models.FloatField(),
        ),
    ]
