import logging
import os
import zipfile

from django.conf import settings
from django.db.utils import DataError, InternalError, OperationalError, ProgrammingError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from celery import shared_task

from daiquiri.core.tasks import Task
from daiquiri.stats.models import Record


class RunQueryTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super().on_failure(exc, task_id, args, kwargs, einfo)

        # always import daiquiri packages inside the task
        from daiquiri.query.models import QueryJob

        # get logger
        logger = logging.getLogger(__name__)

        # get job_id from the original task args
        job_id = args[0]

        # log raised exception
        logger.error('run_query %s raised an exception (%s)', job_id, exc)

        # set phase and error_summary of the crashed job
        job = QueryJob.objects.get(pk=job_id)
        job.phase = job.PHASE_ERROR
        job.error_summary = str(_('There has been an server error with your job.'))
        job.save()


@shared_task(base=RunQueryTask)
def run_database_query_task(job_id):
    # always import daiquiri packages inside the task
    from daiquiri.core.adapter import DatabaseAdapter
    from daiquiri.query.models import QueryJob
    from daiquiri.query.utils import (
        get_job_columns,
        get_job_sources,
        get_quota,
        ingest_uploads,
    )
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
        job.pid = adapter.fetch_pid()
        job.actual_query = adapter.build_query(
            job.schema_name,
            job.table_name,
            job.native_query,
            job.timeout,
            job.max_records,
        )
        job.phase = job.PHASE_EXECUTING
        job.start_time = now()
        job.save()

        logger.info('job %s started', job.id)

        # get the actual query and submit the job to the database
        try:
            job.metadata['upload_columns'] = ingest_uploads(job.uploads, job.owner)

            # this is where the work is done (and the time is spend)
            adapter.submit_query(job.actual_query)

        except (ProgrammingError, InternalError, ValueError, DataError) as e:
            job.phase = job.PHASE_ERROR
            job.error_summary = str(e)
            logger.info('job %s failed (%s)', job.id, job.error_summary)

        except OperationalError as e:
            # load the job again and check if the job was killed
            job = QueryJob.objects.get(pk=job_id)

            if job.phase != job.PHASE_ABORTED:
                job.phase = job.PHASE_ERROR
                job.error_summary = str(e)
                logger.info('job %s failed (%s)', job.id, job.error_summary)

        else:
            # get additional information about the completed job
            job.phase = job.PHASE_COMPLETED
            logger.info('job %s completed', job.id)

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
            job.metadata.pop('upload_columns', None)
            job.metadata.pop('user_columns', None)

            # create a stats record for this job
            Record.objects.create(
                time=job.end_time,
                resource_type='QUERY',
                resource={
                    'job_id': job.id,
                    'job_type': job.job_type,
                },
                client_ip=job.client_ip,
                user=job.owner,
                size=job.size,
            )

            job.save()

    return job.phase


@shared_task(base=Task)
def run_database_ingest_task(job_id, file_path):
    from daiquiri.core.adapter import DatabaseAdapter
    from daiquiri.query.models import QueryJob
    from daiquiri.query.utils import get_quota, ingest_table
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
        job.pid = adapter.fetch_pid()
        job.phase = job.PHASE_EXECUTING
        job.start_time = now()
        job.save()

        logger.info('job %s started', job.id)

        # create the table and insert the data
        try:
            columns = ingest_table(job.schema_name, job.table_name, file_path)

        except (ProgrammingError, InternalError, ValueError) as e:
            job.phase = job.PHASE_ERROR
            job.error_summary = str(e)
            logger.info('job %s failed (%s)', job.id, job.error_summary)

        except OperationalError as e:
            # load the job again and check if the job was killed
            job = QueryJob.objects.get(pk=job_id)
            if job.phase != job.PHASE_ABORTED:
                job.phase = job.PHASE_ERROR
                job.error_summary = str(e)
                logger.info('job %s failed (%s)', job.id, job.error_summary)

        except Exception as e:
            job = QueryJob.objects.get(pk=job_id)
            if job.phase != job.PHASE_ABORTED:
                job.phase = job.PHASE_ERROR
                job.error_summary = 'Unknown error. Please contact the maintainers of this site if the error persists.'
                logger.info('job %s failed (%s)', job.id, str(e))
        else:
            # get additional information about the completed job
            job.phase = job.PHASE_COMPLETED
            logger.info('job %s completed', job.id)

        finally:
            # get timing and save the job object
            job.end_time = now()

            # get additional information about the completed job
            if job.phase == job.PHASE_COMPLETED:
                job.nrows = adapter.count_rows(job.schema_name, job.table_name)
                job.size = adapter.fetch_size(job.schema_name, job.table_name)

                # store the metadata for the columns from the VOTable
                job.metadata = {'columns': columns}

            # create a stats record for this job
            Record.objects.create(
                time=job.end_time,
                resource_type='UPLOAD',
                resource={
                    'job_id': job.id,
                    'job_type': job.job_type,
                },
                client_ip=job.client_ip,
                user=job.owner,
                size=job.size,
            )

            job.save()

    return job.phase


@shared_task(base=Task)
def create_download_table_task(download_id):
    # always import daiquiri packages inside the task
    from daiquiri.query.models import DownloadJob

    # get logger
    logger = logging.getLogger(__name__)

    # get the job object from the database
    download_job = DownloadJob.objects.get(pk=download_id)

    if download_job.phase == download_job.PHASE_QUEUED:
        # log start
        logger.info('download_job %s started', download_job.file_path)

        # create directory if necessary
        try:
            os.mkdir(os.path.dirname(download_job.file_path))
        except OSError:
            pass

        download_job.phase = download_job.PHASE_EXECUTING
        download_job.start_time = now()
        download_job.save()

        # write file using the generator in the adapter
        if download_job.format_key in ('fits', 'parquet'):
            write_label = 'wb'
        else:
            write_label = 'w'

        try:
            with open(download_job.file_path, write_label) as f:
                for line in download_job.query_job.stream(download_job.format_key):
                    f.write(line)

        except Exception as e:
            download_job.phase = download_job.PHASE_ERROR
            download_job.error_summary = str(e)
            download_job.save()
            logger.info(
                'download_job %s failed (%s)',
                download_job.id,
                download_job.error_summary,
            )

            raise e
        else:
            download_job.phase = download_job.PHASE_COMPLETED
            logger.info('download_job %s completed', download_job.file_path)
            Record.objects.create(
                time=download_job.start_time,
                resource_type='CREATE_FILE',
                resource={
                    'job_id': download_job.id,
                    'job_type': download_job.job_type,
                    'file_path': download_job.file_path,
                },
                client_ip=download_job.client_ip,
                size=os.path.getsize(download_job.file_path),
            )
        finally:
            download_job.end_time = now()
            download_job.save()


@shared_task(track_started=True, base=Task)
def create_download_archive_task(archive_id):
    # always import daiquiri packages inside the task
    from daiquiri.query.models import QueryArchiveJob

    # get logger
    logger = logging.getLogger(__name__)

    # get the job object from the database
    archive_job = QueryArchiveJob.objects.get(pk=archive_id)

    if archive_job.phase == archive_job.PHASE_QUEUED:
        # log start
        logger.info('create_archive_zip_file %s started', archive_job.file_path)

        # create directory if necessary
        try:
            os.makedirs(os.path.dirname(archive_job.file_path))
        except OSError:
            pass

        archive_job.phase = archive_job.PHASE_EXECUTING
        archive_job.start_time = now()
        archive_job.save()

        # create a zipfile with all files
        try:
            with zipfile.ZipFile(archive_job.file_path, 'w') as z:
                os.chdir(settings.FILES_BASE_PATH)
                for file_path in archive_job.files:
                    z.write(file_path)

        except Exception as e:
            archive_job.phase = archive_job.PHASE_ERROR
            archive_job.error_summary = str(e)
            archive_job.save()
            logger.info('archive_job %s failed (%s)', archive_job.id, archive_job.error_summary)
            raise e

        archive_job.end_time = now()
        archive_job.phase = archive_job.PHASE_COMPLETED
        archive_job.save()
        Record.objects.create(
            time=archive_job.start_time,
            resource_type='CREATE_ZIP',
            resource={
                'job_id': archive_job.id,
                'job_type': archive_job.job_type,
                'file_path': archive_job.file_path,
            },
            client_ip=archive_job.client_ip,
            size=os.path.getsize(archive_job.file_path),
        )

        # log completion
        logger.info('create_archive_zip_file %s completed', archive_job.file_path)


@shared_task(base=Task)
def rename_database_table_task(schema_name, table_name, new_table_name):
    from daiquiri.core.adapter import DatabaseAdapter

    DatabaseAdapter().rename_table(schema_name, table_name, new_table_name)


@shared_task(base=Task)
def drop_database_table_task(schema_name, table_name):
    from daiquiri.core.adapter import DatabaseAdapter

    # drop the corresponding database table, but fail silently
    try:
        DatabaseAdapter().drop_table(schema_name, table_name)
    except ProgrammingError:
        pass


@shared_task(base=Task)
def abort_database_query_task(pid):
    from daiquiri.core.adapter import DatabaseAdapter

    # abort the job on the database
    try:
        DatabaseAdapter().abort_query(pid)
    except OperationalError:
        # the query was probably killed before
        pass
