# Generated by Django 2.0.3 on 2018-11-10 20:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_auto_20181103_0107'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='fb_user_id',
        ),
        migrations.RemoveField(
            model_name='users',
            name='google_user_id',
        ),
    ]