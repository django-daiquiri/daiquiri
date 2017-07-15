from __future__ import absolute_import, unicode_literals

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

from django.db.utils import OperationalError, ProgrammingError
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _


@shared_task
def submit_query(job_id):
    from daiquiri.core.adapter import get_adapter
    from daiquiri.query.models import QueryJob
    from daiquiri.uws.settings import PHASE_EXECUTING, PHASE_COMPLETED, PHASE_ERROR, PHASE_ABORTED

    # get the job object from the database
    job = QueryJob.objects.get(pk=job_id)

    # get the adapter with the database specific functions
    adapter = get_adapter()

    # create the database of the user if it not already exists
    try:
        adapter.database.create_user_database_if_not_exists(job.database_name)
    except OperationalError as e:
        job.phase = PHASE_ERROR
        job.error_summary = str(e)
        job.save()

        return job.phase

    # set database and start time
    job.start_time = now()

    job.pid = adapter.database.fetch_pid()
    job.actual_query = adapter.database.build_query(job.database_name, job.table_name, job.actual_query)
    job.phase = PHASE_EXECUTING
    job.start_time = now()
    job.save()

    # get the actual query and submit the job to the database
    try:
        # this is where the work ist done (and the time is spend)
        adapter.database.execute(job.actual_query)

    except ProgrammingError as e:
        job.phase = PHASE_ERROR
        job.error_summary = str(e)

    except OperationalError as e:
        # load the job again and check if the job was killed
        job = QueryJob.objects.get(pk=job_id)

        if job.phase != PHASE_ABORTED:
            job.phase = PHASE_ERROR
            job.error_summary = str(e)

    except SoftTimeLimitExceeded:
        job.phase = PHASE_ERROR
        job.error_summary = _('The query exceeded the timelimit for this queue.')

    else:
        # get additional information about the completed job
        job.phase = PHASE_COMPLETED

    finally:
        # get timing and save the job object
        job.end_time = now()
        job.execution_duration = (job.end_time - job.start_time).seconds

        # get additional information about the completed job
        if job.phase == PHASE_COMPLETED:
            job.nrows, job.size = adapter.database.fetch_stats(job.database_name, job.table_name)
            job.metadata = adapter.database.fetch_table(job.database_name, job.table_name)
            job.metadata['columns'] = adapter.database.fetch_columns(job.database_name, job.table_name)

        job.save()

    return job.phase


@shared_task(track_started=True)
def create_download_file(file_name, format_key, database_name, table_name, metadata):
    from daiquiri.core.adapter import get_adapter

    with open(file_name, 'w') as f:
        get_adapter().download.write(f, format_key, database_name, table_name, metadata)
