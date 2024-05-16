# Generated by Django 5.0.4 on 2024-05-16 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_delete_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermanage',
            name='address_index',
            field=models.IntegerField(default='', unique=True, verbose_name='Почтовый индекс'),
        ),
        migrations.AlterField(
            model_name='usermanage',
            name='iin',
            field=models.IntegerField(default='', unique=True, verbose_name='ИИН'),
        ),
    ]
