# Generated by Django 4.1.3 on 2022-12-18 13:49

import authentication.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('CRM', '0019_alter_client_sales_contact_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='sales_contact',
            field=models.ForeignKey(choices=[(29, authentication.models.User.__str__), (28, authentication.models.User.__str__)], on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 18, 13, 49, 23, 457800)),
        ),
        migrations.AlterField(
            model_name='contract',
            name='date_updated',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 18, 13, 49, 23, 457809)),
        ),
    ]
