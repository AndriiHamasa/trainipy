from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trainipy.settings")
app = Celery("trainipy", broker="redis://localhost:6379/0")

app.conf.enable_utc = False
app.conf.update(timezone="Europe/Kiev")

app.config_from_object("django.conf:settings")

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
