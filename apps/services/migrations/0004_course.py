# Generated by Django 4.0.3 on 2023-12-11 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_exams_source_video_solution_premium'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('image', models.ImageField(upload_to='course/')),
                ('url', models.URLField()),
            ],
        ),
    ]
