# Generated by Django 4.0.3 on 2024-12-12 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='label',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
