# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-12 11:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('daiquiri_jobs', '0012_meta'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchiveJob',
            fields=[
                ('job_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='daiquiri_jobs.Job')),
                ('data', jsonfield.fields.JSONField(help_text='Input data for archive creation.', verbose_name='Data')),
                ('files', jsonfield.fields.JSONField(help_text='List of files in the archive.', verbose_name='Files')),
                ('file_path', models.CharField(help_text='Path to the archive file.', max_length=256, verbose_name='Path')),
            ],
            options={
                'ordering': ('start_time',),
                'verbose_name': 'ArchiveJob',
                'verbose_name_plural': 'ArchiveJobs',
                'permissions': (('view_archivejob', 'Can view ArchiveJob'),),
            },
            bases=('daiquiri_jobs.job',),
        ),
    ]