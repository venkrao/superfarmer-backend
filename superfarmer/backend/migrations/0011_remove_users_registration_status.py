# Generated by Django 2.0.3 on 2018-10-28 09:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_auto_20181028_1048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='registration_status',
        ),
    ]
