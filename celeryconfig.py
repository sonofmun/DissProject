__author__ = 'matt'

BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT=['json', 'pickle']
CELERY_TIMEZONE = 'Europe/Oslo'
CELERY_ENABLE_UTC = True
#CELERY_ACKS_LATE = True
#CELERYD_PREFETCH_MULTIPLIER = 1
#CELERY_IGNORE_RESULT = True
