# Generated by Django 4.1.3 on 2022-12-16 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0009_event_notes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='notes',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
