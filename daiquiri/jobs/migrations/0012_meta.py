# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-15 13:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daiquiri_jobs', '0011_job_client_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_type',
            field=models.CharField(choices=[('SYNC', 'Syncronous'), ('ASYNC', 'Asyncronous'), ('INTERFACE', 'Interface')], max_length=10),
        ),
    ]
