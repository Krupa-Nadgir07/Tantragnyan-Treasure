from django.contrib import admin
from django.urls import path
from . import views 
# from .views import leetcode_status_view

urlpatterns = [
    path('',views.sign_in,name='sign_in' ),
    path('sign_up/',views.sign_up,name='sign_up' ),
    path('sign_in/',views.sign_in,name='sign_in' ),
    path('cp_account_info/', views.cp_acc_info, name='cp_account_info'),
    # path('leetcode_status/<int:learner_id>/', leetcode_status_view, name='leetcode_status'),
    path('domain_interested/',views.domain_interested,name='domain_interested' ),
    path('strong_weak_topics/',views.strong_weak_topics,name='strong_weak_topics' ),
    path('dashboard/',views.dashboard,name='dashboard' ),
    path('solved/',views.solved,name='solved' ),
    path('attempted/',views.attempted,name='attempted' ),
    path('bookmarks/',views.bookmarks,name='bookmarks' ),
    path('topics/',views.topics,name='topics' ),
    path('goals/',views.goals,name='goals' ),
    path('new_goal/',views.new_goal,name='new_goal' ),
    path('create_study_group/',views.create_study_group,name='create_study_group' ),
    path('study_group/',views.study_group,name='study_group' ),
    path('sync/<str:platform>/<str:status>/', views.sync_cp_account, name='sync_cp_account'),
    path('schedule_meeting/', views.schedule_meeting, name='schedule_meeting'),
    path('plan-activity/', views.plan_activity, name='plan_activity'),
    path('my_domains/', views.my_domains, name='my_domains'),
]
