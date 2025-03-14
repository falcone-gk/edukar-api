# Generated by Django 4.0.3 on 2024-11-15 01:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0006_alter_exams_source_exam'),
    ]

    operations = [
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('siglas', models.CharField(max_length=25)),
                ('exam_types', models.JSONField(default=list)),
                ('exam_areas', models.JSONField(default=list)),
            ],
        ),
        migrations.RemoveField(
            model_name='exams',
            name='root',
        ),
        migrations.AddField(
            model_name='exams',
            name='area',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='exams',
            name='type',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.DeleteModel(
            name='UnivExamsStructure',
        ),
        migrations.AddField(
            model_name='exams',
            name='university',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.university'),
        ),
    ]
