# Generated by Django 4.0.3 on 2025-01-02 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_exams_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='university',
            name='exam_areas',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
