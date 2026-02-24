from django.urls import path
from . import views

app_name = 'assessments'
urlpatterns = [
    path('', views.assessment_list, name='assessment_list'),
    path('<int:pk>/', views.assessment_detail, name='assessment_detail'),
    path('<int:pk>/start/', views.start_assessment, name='start_assessment'),
    path('attempt/<int:attempt_id>/', views.take_assessment, name='take_assessment'),
    path('result/<int:attempt_id>/', views.assessment_result, name='assessment_result'),
    path('my-badges/', views.my_badges, name='my_badges'),
]
