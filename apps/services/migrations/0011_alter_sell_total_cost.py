# Generated by Django 4.0.3 on 2024-12-05 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_package_product_sell_package_products_exams_packages_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sell',
            name='total_cost',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
