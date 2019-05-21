import logging
import os
import zipfile

from astropy.io.votable import parse_single_table
from celery import shared_task

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError, InternalError
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.tasks import Task


class RunQueryTask(Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(RunQueryTask, self).on_failure(exc, task_id, args, kwargs, einfo)

        # always import daiquiri packages inside the task
        from daiquiri.query.models import QueryJob

        # get logger
        logger = logging.getLogger(__name__)

        # get job_id from the original task args
        job_id = args[0]

        # log raised exception
        logger.error('run_query %s raised an exception (%s)' % (job_id, exc))

        # set phase and error_summary of the crashed job
        job = QueryJob.objects.get(pk=job_id)
        job.phase = job.PHASE_ERROR
        job.error_summary = str(_('There has been an server error with your job.'))
        job.save()


@shared_task(base=RunQueryTask)
def run_query(job_id):
    # always import daiquiri packages inside the task
    from daiquiri.core.adapter import DatabaseAdapter
    from daiquiri.query.models import QueryJob
    from daiquiri.query.utils import get_quota, get_job_sources, get_job_columns
    from daiquiri.stats.models import Record

    # get logger
    logger = logging.getLogger(__name__)

    # get the job object from the database
    job = QueryJob.objects.get(pk=job_id)

    if job.phase == job.PHASE_QUEUED:
        # get the adapter with the database specific functions
        adapter = DatabaseAdapter()

        # create the database of the user if it not already exists
        try:
            adapter.create_user_schema_if_not_exists(job.schema_name)
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

        job.pid = adapter.fetch_pid()
        job.actual_query = adapter.build_query(job.schema_name, job.table_name, job.native_query, job.timeout, job.max_records)
        job.phase = job.PHASE_EXECUTING
        job.start_time = now()
        job.save()

        logger.info('job %s started' % job.id)

        # get the actual query and submit the job to the database
        try:
            # this is where the work ist done (and the time is spend)
            adapter.submit_query(job.actual_query)

        except (ProgrammingError, InternalError) as e:
            job.phase = job.PHASE_ERROR
            job.error_summary = str(e)
            logger.info('job %s failed (%s)' % (job.id, job.error_summary))

        except OperationalError as e:
            # load the job again and check if the job was killed
            job = QueryJob.objects.get(pk=job_id)

            if job.phase != job.PHASE_ABORTED:
                job.phase = job.PHASE_ERROR
                job.error_summary = str(e)
                logger.info('job %s failed (%s)' % (job.id, job.error_summary))

        else:
            # get additional information about the completed job
            job.phase = job.PHASE_COMPLETED
            logger.info('job %s completed' % job.id)

        finally:
            # get timing and save the job object
            job.end_time = now()

            # get additional information about the completed job
            if job.phase == job.PHASE_COMPLETED:
                job.nrows = adapter.count_rows(job.schema_name, job.table_name)
                job.size = adapter.fetch_size(job.schema_name, job.table_name)

                # fetch the metadata for used tables
                job.metadata['sources'] = get_job_sources(job)

                # fetch the metadata for the columns and fetch additional metadata from the metadata store
                job.metadata['columns'] = get_job_columns(job)

            # remove unneeded metadata
            job.metadata.pop('display_columns', None)
            job.metadata.pop('tables', None)

            # create a stats record for this job
            Record.objects.create(
                time=job.end_time,
                resource_type='QUERY',
                resource={
                    'job_id': job.id,
                    'job_type': job.job_type,
                    'query': job.query,
                    'query_language': job.query_language,
                    'sources': job.metadata.get('sources', [])
                },
                client_ip=job.client_ip,
                user=job.owner
            )

            job.save()

    return job.phase


@shared_task(base=Task)
def create_download_file(download_id):
    # always import daiquiri packages inside the task
    from daiquiri.query.models import DownloadJob

    # get logger
    logger = logging.getLogger(__name__)

    # get the job object from the database
    download_job = DownloadJob.objects.get(pk=download_id)

    if download_job.phase == download_job.PHASE_QUEUED:
        # log start
        logger.info('download_job %s started' % download_job.file_path)

        # create directory if necessary
        try:
            os.mkdir(os.path.dirname(download_job.file_path))
        except OSError:
            pass

        download_job.phase = download_job.PHASE_EXECUTING
        download_job.start_time = now()
        download_job.save()

        # write file using the generator in the adapter
        if download_job.format_key == 'fits':
            write_label = 'wb'
        else:
            write_label = 'w'
        try:

            with open(download_job.file_path, write_label) as f:
                for line in download_job.job.stream(download_job.format_key):
                    f.write(line)

        except Exception as e:
            download_job.phase = download_job.PHASE_ERROR
            download_job.error_summary = str(e)
            download_job.save()
            logger.info('download_job %s failed (%s)' % (download_job.id, download_job.error_summary))
        else:
            download_job.phase = download_job.PHASE_COMPLETED
            logger.info('download_job %s completed' % download_job.file_path)
        finally:
            download_job.end_time = now()
            download_job.save()


@shared_task(track_started=True, base=Task)
def create_archive_file(archive_id):
    # always import daiquiri packages inside the task
    from daiquiri.query.models import QueryArchiveJob

    # get logger
    logger = logging.getLogger(__name__)

    # get the job object from the database
    archive_job = QueryArchiveJob.objects.get(pk=archive_id)

    if archive_job.phase == archive_job.PHASE_QUEUED:
        # log start
        logger.info('create_archive_zip_file %s started' % archive_job.file_path)

        # create directory if necessary
        try:
            os.makedirs(os.path.dirname(archive_job.file_path))
        except OSError:
            pass

        archive_job.phase = archive_job.PHASE_EXECUTING
        archive_job.start_time = now()
        archive_job.save()

        # create a zipfile with all files
        with zipfile.ZipFile(archive_job.file_path, 'w') as z:
            os.chdir(settings.FILES_BASE_PATH)
            for file_path in archive_job.files:
                z.write(file_path)

        archive_job.end_time = now()
        archive_job.phase = archive_job.PHASE_COMPLETED
        archive_job.save()

        # log completion
        logger.info('create_archive_zip_file %s completed' % archive_job.file_path)


@shared_task(base=Task)
def rename_table(schema_name, table_name, new_table_name):
    from daiquiri.core.adapter import DatabaseAdapter

    DatabaseAdapter().rename_table(schema_name, table_name, new_table_name)


@shared_task(base=Task)
def drop_table(schema_name, table_name):
    from daiquiri.core.adapter import DatabaseAdapter

    # drop the corresponding database table, but fail silently
    try:
        DatabaseAdapter().drop_table(schema_name, table_name)
    except ProgrammingError:
        pass


@shared_task(base=Task)
def abort_query(pid):
    from daiquiri.core.adapter import DatabaseAdapter

    # abort the job on the database
    try:
        DatabaseAdapter().abort_query(pid)
    except OperationalError:
        # the query was probably killed before
        pass


@shared_task(base=Task)
def ingest_table(job_id, file_path):
    from daiquiri.core.adapter import DatabaseAdapter
    from daiquiri.query.models import QueryJob
    from daiquiri.stats.models import Record

    # get the job object from the database
    job = QueryJob.objects.get(pk=job_id)

    # parse the uploaded table
    table = parse_single_table(file_path)

    # obtain the column names and (vo) datatypes from the table
    columns = []
    for field in table.fields:
        columns.append({
            'name': field.name,
            'datatype': field.datatype,
            'ucd': field.ucd,
            'unit': str(field.unit),
        })

    # get the adapter with the database specific functions
    adapter = DatabaseAdapter()

    # create the table and insert the data
    adapter.create_table(job.schema_name, job.table_name, columns)
    adapter.insert_rows(job.schema_name, job.table_name, columns, table.array)

    job.phase = job.PHASE_COMPLETED

    # get timing and save the job object
    job.end_time = now()

    # get additional information about the completed job
    if job.phase == job.PHASE_COMPLETED:
        job.nrows = adapter.count_rows(job.schema_name, job.table_name)
        job.size = adapter.fetch_size(job.schema_name, job.table_name)

        # fetch the metadata for the columns
        job.metadata = {
            'columns': columns
        }

    # create a stats record for this job
    Record.objects.create(
        time=job.end_time,
        resource_type='UPLOAD',
        resource={
            'job_id': job.id,
            'job_type': job.job_type,
        },
        client_ip=job.client_ip,
        user=job.owner
    )

    job.save()
