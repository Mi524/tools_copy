# Generated by Django 3.1.7 on 2021-02-26 06:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_tables', '0004_auto_20210226_1102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inputdata',
            name='insert_complete',
        ),
    ]
