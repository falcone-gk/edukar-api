# Generated by Django 4.0.3 on 2024-05-07 13:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_profile_picture'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserImage',
        ),
    ]
