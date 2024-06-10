from django.core.management.base import BaseCommand
from celery import Celery


class Command(BaseCommand):
    help = 'Runs the Celery worker with Gevent pool and autoscaling'

    def handle(self, *args, **kwargs):
        app = Celery('zavod')
        app.config_from_object('django.conf:settings', namespace='CELERY')
        app.autodiscover_tasks()

        app.worker_main(argv=['worker', '--loglevel=info', '-P', 'gevent', '--autoscale=10,3'])
