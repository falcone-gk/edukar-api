# Generated by Django 4.0.3 on 2024-05-08 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0009_comment_image_post_image_reply_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='body',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='body',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='reply',
            name='body',
            field=models.TextField(blank=True),
        ),
    ]
