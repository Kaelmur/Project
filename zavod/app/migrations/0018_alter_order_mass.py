# Generated by Django 5.0.4 on 2024-05-11 19:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_alter_fractionprice_price_alter_order_mass'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='mass',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Масса щебня (тонн)'),
        ),
    ]
