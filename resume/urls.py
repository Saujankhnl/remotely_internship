from django.urls import path
from . import views

app_name = 'resume'
urlpatterns = [
    path('', views.resume_builder, name='resume_builder'),
    path('generate/', views.generate_resume_pdf, name='generate_pdf'),
    path('preview/<str:template_name>/', views.resume_preview, name='resume_preview'),
    path('my-resumes/', views.my_resumes, name='my_resumes'),
    path('delete/<int:pk>/', views.delete_resume, name='delete_resume'),
]
