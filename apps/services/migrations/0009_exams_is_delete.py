# Generated by Django 4.0.3 on 2024-11-17 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_alter_exams_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='exams',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
    ]
