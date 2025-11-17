"""
Forum URL configuration.
"""
from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:forum_slug>/', views.forum_detail, name='forum_detail'),
    path('<slug:category_slug>/<slug:forum_slug>/new/', views.create_topic, name='create_topic'),
    path('<slug:category_slug>/<slug:forum_slug>/<slug:topic_slug>-<int:pk>/', views.topic_detail, name='topic_detail'),
    path('<slug:category_slug>/<slug:forum_slug>/<slug:topic_slug>-<int:pk>/reply/', views.create_post, name='create_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
]
