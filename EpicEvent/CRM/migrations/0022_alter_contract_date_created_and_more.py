# Generated by Django 4.1.3 on 2022-12-23 19:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0021_alter_client_sales_contact_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 23, 19, 38, 48, 308155)),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_updated',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 23, 19, 38, 48, 308164)),
        ),
    ]
