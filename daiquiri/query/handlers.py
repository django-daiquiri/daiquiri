#from django.conf import settings
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import DownloadJob, QueryJob


@receiver(pre_save, sender=QueryJob)
def query_job_updated_handler(sender, **kwargs):
    instance = kwargs['instance']

    try:
        QueryJob.objects.get(pk=instance.pk).rename_table(instance.table_name)
    except QueryJob.DoesNotExist:
        pass


@receiver(post_delete, sender=QueryJob)
def query_job_deleted_handler(sender, **kwargs):
    kwargs['instance'].drop_table()


@receiver(post_delete, sender=DownloadJob)
def download_job_deleted_handler(sender, **kwargs):
    kwargs['instance'].delete_file()
