# Generated by Django 3.1.7 on 2021-02-27 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic_tables', '0010_auto_20210227_1557'),
    ]

    operations = [
        migrations.AlterField(
            model_name='undertaketeam',
            name='undertake_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='undertaketeam',
            name='undertake_team',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
