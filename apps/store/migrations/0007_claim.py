# Generated by Django 4.0.3 on 2025-01-17 23:48

from django.db import migrations, models
import store.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_product_source'),
    ]

    operations = [
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=200)),
                ('dni', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=100)),
                ('phone', models.CharField(max_length=50)),
                ('is_minor', models.BooleanField(default=False)),
                ('proxy_name', models.CharField(blank=True, max_length=100, null=True)),
                ('type_good', models.IntegerField(choices=[(1, 'Producto'), (2, 'Servicio')])),
                ('claim_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField(blank=True)),
                ('claim_detail', models.TextField()),
                ('request', models.TextField()),
                ('claim_file', models.FileField(null=True, upload_to=store.models.Claim.claim_upload_to)),
            ],
        ),
    ]
