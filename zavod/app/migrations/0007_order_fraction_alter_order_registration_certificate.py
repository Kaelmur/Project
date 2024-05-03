# Generated by Django 5.0.4 on 2024-05-03 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_order_date_ordered'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='fraction',
            field=models.CharField(choices=[('0-5', '0-5'), ('5-20', '5-20'), ('20-40', '20-40'), ('5-40', '5-40'), ('40-70', '40-70')], default='0', max_length=100, verbose_name='Фракция щебня'),
        ),
        migrations.AlterField(
            model_name='order',
            name='registration_certificate',
            field=models.CharField(max_length=100, verbose_name='Номер машины'),
        ),
    ]
