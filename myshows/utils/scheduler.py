from apscheduler.schedulers.background import BackgroundScheduler
from myshows.utils import myshows_api


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(myshows_api.parse_news, 'interval', hours=8, max_instances=1)
    scheduler.start()
