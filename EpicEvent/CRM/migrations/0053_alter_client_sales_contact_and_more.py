# Generated by Django 4.1.3 on 2023-01-02 08:58

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CRM', '0052_alter_contract_date_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='sales_contact',
            field=models.ForeignKey(limit_choices_to={'groups__name': 'Sales team'}, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 2, 8, 58, 34, 707969)),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_updated',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 2, 8, 58, 34, 707977)),
        ),
    ]