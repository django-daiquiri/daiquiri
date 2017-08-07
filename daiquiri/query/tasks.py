from __future__ import absolute_import, unicode_literals

from celery import shared_task

from django.db.utils import OperationalError, ProgrammingError, InternalError
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _


@shared_task
def run_query(job_id):
    import logging

    from daiquiri.core.adapter import get_adapter
    from daiquiri.query.models import QueryJob
    from daiquiri.query.utils import get_quota

    # get logger
    logger = logging.getLogger(__name__)

    # get the job object from the database
    job = QueryJob.objects.get(pk=job_id)

    # get the adapter with the database specific functions
    adapter = get_adapter()

    # create the database of the user if it not already exists
    try:
        adapter.database.create_user_database_if_not_exists(job.database_name)
    except OperationalError as e:
        job.phase = job.PHASE_ERROR
        job.error_summary = str(e)
        job.save()

        return job.phase

    # check if the quota is exceeded
    if QueryJob.objects.get_size(job.owner) > get_quota(job.owner):
        job.phase = job.PHASE_ERROR
        job.error_summary = str(_('Quota is exceeded. Please remove some of your jobs.'))
        job.save()

        return job.phase

    # set database and start time
    job.start_time = now()

    job.pid = adapter.database.fetch_pid()
    job.actual_query = adapter.database.build_query(job.database_name, job.table_name, job.native_query, job.timeout, job.max_records)
    job.phase = job.PHASE_EXECUTING
    job.start_time = now()
    job.save()

    logger.info('run_query %s started' % job.id)

    # get the actual query and submit the job to the database
    try:
        # this is where the work ist done (and the time is spend)
        adapter.database.execute(job.actual_query)

    except (ProgrammingError, InternalError) as e:
        job.phase = job.PHASE_ERROR
        job.error_summary = str(e)
        logger.info('run_query %s failed (%s)' % (job.id, job.error_summary))

    except OperationalError as e:
        # load the job again and check if the job was killed
        job = QueryJob.objects.get(pk=job_id)

        if job.phase != job.PHASE_ABORTED:
            job.phase = job.PHASE_ERROR
            job.error_summary = str(e)
            logger.info('run_query %s failed (%s)' % (job.id, job.error_summary))

    else:
        # get additional information about the completed job
        job.phase = job.PHASE_COMPLETED
        logger.info('run_query %s completed' % job.id)

    finally:
        # get timing and save the job object
        job.end_time = now()
        job.execution_duration = (job.end_time - job.start_time).seconds

        # get additional information about the completed job
        if job.phase == job.PHASE_COMPLETED:
            job.nrows, job.size = adapter.database.fetch_stats(job.database_name, job.table_name)
            job.metadata = adapter.database.fetch_table(job.database_name, job.table_name)
            job.metadata['columns'] = adapter.database.fetch_columns(job.database_name, job.table_name)

        job.save()

    return job.phase


@shared_task(track_started=True)
def create_download_file(file_name, format_key, database_name, table_name, metadata, status, empty):
    import logging

    from daiquiri.core.adapter import get_adapter

    # get logger
    logger = logging.getLogger(__name__)
    logger.info('create_download_file %s started' % file_name)

    with open(file_name, 'w') as f:
        for line in get_adapter().download.generate(format_key, database_name, table_name, metadata, status, empty):
            f.write(line)

    logger.info('create_download_file %s completed' % file_name)
