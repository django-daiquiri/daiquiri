from kombu import Exchange, Queue

import daiquiri.core.env as env

CELERY_BROKER_URL = env.get('CELERY_BROKER_URL', 'amqp://')

CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

CELERY_TASK_DEFAULT_QUEUE = 'default'

CELERY_TASK_QUEUES = [
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('download', Exchange('download'), routing_key='download'),
    Queue('query', Exchange('query'), routing_key='query', queue_arguments={
        'x-max-priority': 5
    })
]
