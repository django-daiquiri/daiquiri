from __future__ import unicode_literals

from django.db import migrations


def run_data_migration(apps, schema_editor):
    QueryJob = apps.get_model('daiquiri_query', 'QueryJob')

    for queryjob in QueryJob.objects.filter(job_type='SYNC'):
        queryjob.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('daiquiri_query', '0018_blank_metadata'),
        ('daiquiri_stats', '0002_data_migration'),
    ]

    operations = [
        migrations.RunPython(run_data_migration)
    ]
