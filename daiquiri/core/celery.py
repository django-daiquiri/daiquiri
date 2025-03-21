from django.conf import settings

from celery import Celery
from kombu import Exchange, Queue


def get_celery_app():
    app = Celery(settings.DAIQUIRI_APP)

    # configure celery and add apps
    app.conf.broker_url = settings.CELERY_BROKER_URL
    app.conf.worker_prefetch_multiplier = 1
    app.conf.task_acks_late = True

    # configure queues
    queues = [
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('download', Exchange('download'), routing_key='download')
    ]
    for queue in settings.QUERY_QUEUES:
        queue_name = exchange_name = routing_key = 'query.{key}'.format(**queue)
        queue = Queue(queue_name, Exchange(exchange_name), routing_key=routing_key)
        queues.append(queue)

    app.conf.task_default_queue = 'default'
    app.conf.task_queues = queues

    # load task modules from all registered Django app configs
    app.autodiscover_tasks()

    return app
