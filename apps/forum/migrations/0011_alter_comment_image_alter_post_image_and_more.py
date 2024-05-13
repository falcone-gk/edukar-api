# Generated by Django 4.0.3 on 2024-05-12 06:03

from django.db import migrations
import django_resized.forms
import forum.models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0010_alter_comment_body_alter_post_body_alter_reply_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='WebP', keep_meta=True, null=True, quality=50, scale=None, size=[800, 400], upload_to=forum.models.BaseContentPublication.image_upload),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='WebP', keep_meta=True, null=True, quality=50, scale=None, size=[800, 400], upload_to=forum.models.BaseContentPublication.image_upload),
        ),
        migrations.AlterField(
            model_name='reply',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format='WebP', keep_meta=True, null=True, quality=50, scale=None, size=[800, 400], upload_to=forum.models.BaseContentPublication.image_upload),
        ),
    ]