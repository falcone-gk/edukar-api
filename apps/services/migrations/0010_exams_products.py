# Generated by Django 4.0.3 on 2024-12-12 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
        ('services', '0009_exams_is_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='exams',
            name='products',
            field=models.ManyToManyField(related_name='exams', to='store.product'),
        ),
    ]