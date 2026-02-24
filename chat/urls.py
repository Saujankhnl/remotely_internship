from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<int:application_id>/', views.chat_room, name='chat_room'),
    path('api/send/<int:room_id>/', views.send_message_ajax, name='send_message'),
    path('api/messages/<int:room_id>/', views.fetch_messages_ajax, name='fetch_messages'),
    path('api/upload/<int:room_id>/', views.upload_attachment, name='upload_attachment'),
]
