# Generated by Django 4.0.3 on 2024-11-16 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0007_university_remove_exams_root_exams_area_exams_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exams',
            name='slug',
            field=models.SlugField(max_length=125, unique=True),
        ),
    ]
