# Generated by Django 2.1.1 on 2018-11-01 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_auto_20181101_1316'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datareferal',
            options={'ordering': ['profit_from_friends'], 'verbose_name': 'Данные по рефреалу', 'verbose_name_plural': 'Данные по рефреалам'},
        ),
        migrations.RemoveField(
            model_name='datareferal',
            name='count_friends',
        ),
    ]
