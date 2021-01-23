from django.urls import path

from myshows.views import views

urlpatterns = [
    # ex: /myshows/
    path('', views.index, name='index'),
    # ex: /myshows/5/
    path('<int:pk>/', views.ShowDetailView.as_view(), name='detail'),
    # ex: /myshows/search/
    path('search/', views.SearchShowListView.as_view(), name='search'),
    # ex: /myshows/all/
    path('all/', views.ShowListView.as_view(), name='all'),
]