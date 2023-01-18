# Generated by Django 4.1.3 on 2023-01-18 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0066_remove_event_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='contract',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='CRM.contract'),
            preserve_default=False,
        ),
    ]
