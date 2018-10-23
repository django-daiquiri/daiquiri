from __future__ import unicode_literals

from django.db import migrations


def run_data_migration(apps, schema_editor):
    QueryJob = apps.get_model('daiquiri_query', 'QueryJob')
    Record = apps.get_model('daiquiri_stats', 'Record')

    for record in Record.objects.all():
        if record.resource_type == 'QUERY_JOB':
            try:
                job = QueryJob.objects.get(pk=record.resource['job_id'])
                record.resource['query'] = job.query
                record.resource['query_language'] = job.query_language

            except QueryJob.DoesNotExist:
                record.resource['job_id'] = None
                record.resource['query'] = None
                record.resource['query_language'] = None

            record.resource_type = 'QUERY'
            record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('daiquiri_stats', '0002_data_migration'),
        ('daiquiri_query', '0013_refactoring'),
    ]

    operations = [
        migrations.RunPython(run_data_migration)
    ]
