# Generated by Django 4.1.3 on 2023-01-04 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0059_alter_contract_sales_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CRM.client', unique=True),
        ),
    ]
