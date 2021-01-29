import os

from django.apps import AppConfig


class MyshowsConfig(AppConfig):
    name = 'myshows'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':
            from myshows.utils import scheduler
            scheduler.start()
