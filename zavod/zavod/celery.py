from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zavod.settings')

app = Celery('zavod')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.enable_utc = False

app.conf.update(timezone='Asia/Almaty')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
