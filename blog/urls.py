from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('post/<slug:slug>/', views.blog_post, name='blog_post'),
    path('newsletter/subscribe/', views.subscribe, name='subscribe'),
    path('newsletter/unsubscribe/<uuid:subscriber_id>/', views.unsubscribe, name='unsubscribe'),
    path('search/', views.blog_search, name='blog_search'),
]