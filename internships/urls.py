from django.urls import path
from . import views

app_name = 'internships'

urlpatterns = [
    # Public views
    path('', views.internship_list, name='internship_list'),
    path('<int:pk>/', views.internship_detail, name='internship_detail'),
    
    # Company views - Internship management
    path('create/', views.create_internship, name='create_internship'),
    path('<int:pk>/edit/', views.edit_internship, name='edit_internship'),
    path('<int:pk>/delete/', views.delete_internship, name='delete_internship'),
    path('<int:pk>/toggle-status/', views.toggle_internship_status, name='toggle_status'),
    path('my-internships/', views.my_internships, name='my_internships'),
    
    # Company views - Application management
    path('<int:pk>/applications/', views.view_applications, name='view_applications'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
    path('application/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    
    # User views
    path('<int:pk>/apply/', views.apply_internship, name='apply_internship'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:pk>/withdraw/', views.withdraw_application, name='withdraw_application'),
]
