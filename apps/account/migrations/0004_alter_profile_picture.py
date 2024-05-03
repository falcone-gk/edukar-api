# Generated by Django 4.0.3 on 2024-05-02 20:50

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_userimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(default='default-avatar.jpg', upload_to=account.models.Profile.image_upload),
        ),
    ]
