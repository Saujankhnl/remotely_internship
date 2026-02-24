from django.urls import path

from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('api/count/', views.notification_count_api, name='notification_count'),
    path('api/preview/', views.notification_preview_api, name='notification_preview'),
    path('<int:pk>/read/', views.mark_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
]
