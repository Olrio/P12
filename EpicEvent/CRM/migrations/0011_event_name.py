# Generated by Django 4.1.3 on 2022-12-16 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0010_alter_event_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='name',
            field=models.CharField(default='My Event', max_length=250),
            preserve_default=False,
        ),
    ]
