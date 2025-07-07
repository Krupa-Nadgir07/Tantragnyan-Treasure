from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('learner/',include('learners.urls') ),
    # path('study_groups/',include('study_group.urls') ),
    path('blogs/',include('blogging.urls') ),
    path('',views.home, name='home'),
    path('topics/',views.topics, name='topics'),
    path('topics/<int:pid>/', views.topic_page, name='topic_page'),
]