# Generated by Django 4.1.3 on 2022-12-05 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0003_client_company_name_client_date_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='date_updated',
            field=models.DateTimeField(verbose_name='Client Date Updated'),
        ),
    ]
