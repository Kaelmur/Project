# Generated by Django 5.0.4 on 2024-05-09 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_pay_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='manufactory',
            field=models.CharField(choices=[('4 цех', '4 цех'), ('ЦПШ', 'ЦПШ')], default='4 цех', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='fraction',
            field=models.CharField(choices=[('0-5', '0-5'), ('5-20', '5-20'), ('20-40', '20-40'), ('5-40', '5-40'), ('40-70', '40-70'), ('Бутовый камень', 'Бутовый камень')], default='0', max_length=100, verbose_name='Фракция щебня'),
        ),
    ]
