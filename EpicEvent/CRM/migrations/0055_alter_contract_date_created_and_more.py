# Generated by Django 4.1.3 on 2023-01-02 20:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0054_alter_contract_date_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 2, 20, 51, 27, 930496)),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_updated',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 2, 20, 51, 27, 930503)),
        ),
    ]
