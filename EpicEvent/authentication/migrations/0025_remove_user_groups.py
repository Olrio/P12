# Generated by Django 4.1.3 on 2022-12-28 22:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0024_user_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='groups',
        ),
    ]