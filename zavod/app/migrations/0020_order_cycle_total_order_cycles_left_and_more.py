# Generated by Django 5.0.4 on 2024-05-16 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_alter_order_mass'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cycle_total',
            field=models.CharField(default=1, max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='cycles_left',
            field=models.CharField(default=1, max_length=20),
        ),
        migrations.AlterField(
            model_name='fractionprice',
            name='fraction',
            field=models.CharField(choices=[('0-5', '0-5'), ('5-20', '5-20'), ('20-40', '20-40'), ('5-40', '5-40'), ('40-70', '40-70'), ('Бутовый камень', 'Бутовый камень')], max_length=100),
        ),
        migrations.AlterField(
            model_name='fractionprice',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
