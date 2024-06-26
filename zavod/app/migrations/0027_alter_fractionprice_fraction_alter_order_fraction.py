# Generated by Django 5.0.4 on 2024-06-04 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_alter_fractionprice_fraction_alter_order_fraction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fractionprice',
            name='fraction',
            field=models.CharField(choices=[('0-5', '0-5'), ('5-20', '5-20'), ('20-40', '20-40'), ('5-40', '5-40'), ('40-70', '40-70'), ('Бутовый камень', 'Бутовый камень')], max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='fraction',
            field=models.CharField(choices=[('0-5', '0-5'), ('5-20', '5-20'), ('20-40', '20-40'), ('5-40', '5-40'), ('40-70', '40-70'), ('Бутовый камень', 'Бутовый камень')], default='0', max_length=100, verbose_name='Фракция щебня'),
        ),
    ]
