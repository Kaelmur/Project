# Generated by Django 5.0.4 on 2024-05-03 08:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_order_fraction_alter_order_registration_certificate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='mass',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Масса щебня (тонн)'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('done', 'Done'), ('pending', 'Pending'), ('continuing', 'Continuing')], default='неоплачено', max_length=20),
        ),
    ]
