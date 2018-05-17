# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-08 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daiquiri_meetings', '0003_meta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contribution',
            name='contribution_type',
            field=models.CharField(blank=True, help_text='Choices are given by settings.MEETINGS_CONTRIBUTION_TYPES', max_length=8, verbose_name='Contribution type'),
        ),
    ]