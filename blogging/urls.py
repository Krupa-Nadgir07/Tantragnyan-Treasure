from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_home, name='blog_home'),
    path('create_blog_post/', views.create_blog_post, name='create_blog_post'),
    path('view_blogs/<int:pid>', views.blog_list, name='blog_list'),
    path('blog_detail/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('admin/view_blogs/', views.blog_list, name='blog_list'),  # View pending blogs
    path('admin/approve_blog/<int:blog_id>/', views.approve_blog, name='approve_blog'), 
]
