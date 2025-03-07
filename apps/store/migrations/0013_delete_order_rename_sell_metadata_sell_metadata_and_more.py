# Generated by Django 4.0.3 on 2025-03-04 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_productcomment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.RenameField(
            model_name='sell',
            old_name='sell_metadata',
            new_name='metadata',
        ),
        migrations.AddField(
            model_name='sell',
            name='order_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sell',
            name='order_id',
            field=models.CharField(blank=True, editable=False, max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='sell',
            name='order_number',
            field=models.CharField(blank=True, editable=False, max_length=50, unique=True),
        ),
        migrations.AddField(
            model_name='sell',
            name='receipt_number',
            field=models.PositiveIntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='sell',
            name='status',
            field=models.PositiveIntegerField(choices=[(1, 'Aceptado'), (2, 'Pendiente'), (3, 'Fallido')], default=2),
        ),
        migrations.AddField(
            model_name='sell',
            name='user_phone_number',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
