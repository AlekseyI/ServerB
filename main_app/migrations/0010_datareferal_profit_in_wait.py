# Generated by Django 2.1.1 on 2018-11-14 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_auto_20181102_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='datareferal',
            name='profit_in_wait',
            field=models.FloatField(default=0, verbose_name='Прибыль от друзей в ожидании'),
        ),
    ]
