# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-02-17 19:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('daiquiri_auth', '0008_profile_is_pending'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DetailKey',
        ),
    ]