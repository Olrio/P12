# Generated by Django 4.1.3 on 2022-12-30 10:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0049_alter_contract_date_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 30, 10, 44, 7, 791689)),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_updated',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 30, 10, 44, 7, 791697)),
        ),
    ]