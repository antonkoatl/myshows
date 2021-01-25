from django.urls import path

from myshows.views import views

urlpatterns = [
    # ex: /myshows/
    path('', views.index, name='index'),
    # ex: /myshows/5/
    path('<int:pk>/', views.ShowDetailView.as_view(), name='detail'),
    # ex: /myshows/5/1/
    path('<int:pk>/<int:season_number>/', views.ShowDetailView.as_view(), name='detail_season'),
    # ex: /myshows/search/
    path('search/', views.ShowListView.as_view(), name='search'),
    # ex: /myshows/all/
    path('all/', views.ShowListView.as_view(), name='all'),
    # ex: /myshows/news/
    path('news/', views.NewsListView.as_view(), name='news'),
    # ex: /myshows/news/5/
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    # ex: /myshows/ratings/
    path('ratings/', views.RatingsDetailView.as_view(), name='ratings'),
    # ex: /myshows/trivia/
    path('trivia/', views.TriviaView.as_view(), name='trivia'),
    # ex: /myshows/trivia/check
    path('trivia/check', views.check_trivia, name='check_trivia'),
]
