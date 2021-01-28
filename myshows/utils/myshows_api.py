import json
import logging
import urllib
from datetime import datetime

import requests
from django.core.files import File

from myshows.models import Article, User, ArticleImage

url = 'https://api.myshows.me/v2/rpc/'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
log = logging.getLogger(__name__)


def get_news(page):
    params = {
        "jsonrpc": "2.0",
        "method": "news.Get",
        "params": {
            "search": {},
            "page": page,
            "pageSize": 25
        },
        "id": 1
    }

    response = requests.post(url, data=json.dumps(params), headers=headers)

    code = response.status_code
    assert code == 200
    result = json.loads(response.content)
    return result['result']


def get_news_by_id(news_id):
    params = {
        "jsonrpc": "2.0",
        "method": "news.GetById",
        "params": {
            "newsId": news_id
        },
        "id": 1
    }

    response = requests.post(url, data=json.dumps(params), headers=headers)

    code = response.status_code
    assert code == 200
    result = json.loads(response.content)
    return result['result']


def download_image(image, path):
    hash0 = image[:1]
    hash1 = image[1:3]
    image_url = f'https://media.myshows.me/{path}/normal/{hash0}/{hash1}/{image}'
    downloaded = urllib.request.urlretrieve(image_url)
    dj_file = File(open(downloaded[0], 'rb'))
    return dj_file


def _parse_news():
    for i in range(10):
        news = get_news(i)

        for j, article in enumerate(news):
            article = get_news_by_id(article['id'])
            myshows_url = f'https://myshows.me/news/{article["id"]}/{article["alias"]}/'
            if Article.objects.filter(source=myshows_url).exists():
                return

            db_article = Article()
            db_article.title = article['title']
            db_article.foreword = article['foreword']
            db_article.content = article['content']
            db_article.published_at = datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%S%z')
            db_article.author = User.objects.all()[0]
            db_article.video = article['video']
            if article['category']['alias'] not in Article.ArticleCategories:
                raise Exception(f"Article category unknown {article['category']}")
            db_article.category = Article.ArticleCategories(article['category']['alias'])
            db_article.tags = ','.join([x['title'] for x in article['tags']]) if article['tags'] is not None else ''
            db_article.source = myshows_url
            db_article.save()

            for image in article['images']:
                db_image = ArticleImage()
                db_image.article = db_article
                db_image.image.save(image, download_image(image, 'news'))
                db_image.save()

            log.debug(f"myshows parse_news: new article {db_article.title}")


def parse_news():
    log.debug(f"Started parsing news from myshows")
    _parse_news()
    log.debug(f"Finished parsing news from myshows")
