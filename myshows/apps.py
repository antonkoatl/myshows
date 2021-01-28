from django.apps import AppConfig


class MyshowsConfig(AppConfig):
    name = 'myshows'

    def ready(self):
        from myshows.utils import scheduler
        scheduler.start()
