from celery import Task as CeleryTask


class Task(CeleryTask):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        import logging
        logger = logging.getLogger('daiquiri')
        logger.error(einfo)
