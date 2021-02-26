# Generated by Django 3.1.7 on 2021-02-24 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BasicCountry',
            fields=[
                ('country_cn', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('country_en', models.CharField(max_length=4, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InputData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_model', models.CharField(max_length=100, null=True)),
                ('type_of_test', models.CharField(max_length=100)),
                ('details', models.CharField(max_length=200, null=True)),
                ('region', models.CharField(max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('person_day', models.CharField(max_length=20)),
                ('remark', models.CharField(max_length=100, null=True)),
                ('engineer', models.CharField(max_length=100, null=True)),
                ('update_reason', models.TextField(null=True)),
                ('platform_info', models.CharField(max_length=100, null=True)),
                ('status', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestModule',
            fields=[
                ('module_name', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='UndertakeTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_cn', models.CharField(max_length=30, unique=True)),
                ('undertake_team', models.CharField(max_length=200, unique=True)),
                ('undertake_date', models.DateField()),
            ],
            options={
                'unique_together': {('country_cn', 'undertake_team', 'undertake_date')},
            },
        ),
    ]
