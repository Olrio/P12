# Generated by Django 4.1.3 on 2023-01-02 20:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0053_alter_client_sales_contact_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 2, 20, 46, 15, 158773)),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_updated',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 2, 20, 46, 15, 158781)),
        ),
    ]