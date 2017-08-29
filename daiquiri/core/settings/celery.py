from kombu import Exchange, Queue

from .base import DAIQUIRI_APP

default_queue = '%s_default' % DAIQUIRI_APP
download_queue = '%s_download' % DAIQUIRI_APP
query_queue = '%s_query' % DAIQUIRI_APP

CELERY_BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_QUEUES = (
    Queue(default_queue, Exchange(default_queue), routing_key=default_queue),
    Queue(download_queue, Exchange(download_queue), routing_key=download_queue),
    Queue(query_queue, Exchange(query_queue), routing_key=query_queue, queue_arguments={
        'x-max-priority': 5
    })
)
