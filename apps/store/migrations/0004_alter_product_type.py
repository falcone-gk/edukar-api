# Generated by Django 4.0.3 on 2024-12-24 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_product_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='type',
            field=models.PositiveIntegerField(choices=[(1, 'Documento'), (2, 'Video'), (3, 'Paquete')], default=1),
        ),
    ]
