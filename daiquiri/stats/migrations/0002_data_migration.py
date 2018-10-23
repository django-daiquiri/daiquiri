from __future__ import unicode_literals

from django.db import migrations


def migrate_jobs(apps, schema_editor):
    QueryJob = apps.get_model('daiquiri_query', 'QueryJob')
    Record = apps.get_model('daiquiri_stats', 'Record')

    for job in QueryJob.objects.all():
        Record.objects.create(
            time=job.end_time,
            resource_type='QUERY_JOB',
            resource={
                'job_id': job.id,
                'job_type': job.job_type,
                'tables': job.metadata['source_tables'] if 'source_tables' in job.metadata else []
            },
            client_ip=job.client_ip,
            user=job.owner
        )

class Migration(migrations.Migration):

    dependencies = [
        ('daiquiri_stats', '0001_initial'),
        ('daiquiri_jobs', '0012_meta'),
        ('daiquiri_query', '0013_refactoring')
    ]

    operations = [
        migrations.RunPython(migrate_jobs)
    ]
