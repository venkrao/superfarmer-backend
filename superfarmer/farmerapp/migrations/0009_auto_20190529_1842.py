# Generated by Django 2.0.3 on 2019-05-29 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farmerapp', '0008_negotiationrequest_sent_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='negotiationrequest',
            name='id',
        ),
        migrations.AlterField(
            model_name='negotiationrequest',
            name='request_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
