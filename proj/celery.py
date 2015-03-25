from __future__ import absolute_import

from celery import Celery

__author__ = 'matt'

app = Celery('tasks',
             broker='redis://127.0.0.1:6379',
             backend='redis://127.0.0.1:6379')

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
	CELERY_TASK_SERIALIZER='json',
	CELERY_RESULT_SERIALIZER='json'
)

if __name__ == '__main__':
    app.start()