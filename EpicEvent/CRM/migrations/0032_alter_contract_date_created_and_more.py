# Generated by Django 4.1.3 on 2022-12-26 16:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0031_alter_contract_date_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 26, 16, 37, 17, 919266)),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_updated',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 26, 16, 37, 17, 919274)),
        ),
    ]
