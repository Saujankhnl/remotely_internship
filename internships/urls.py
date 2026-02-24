from django.urls import path
from . import views

app_name = 'internships'

urlpatterns = [
    # ==================== INTERNSHIP URLs ====================
    # Public views
    path('', views.internship_list, name='internship_list'),
    path('internship/<int:pk>/', views.internship_detail, name='internship_detail'),
    
    # Company views - Internship management
    path('create/', views.create_internship, name='create_internship'),
    path('internship/<int:pk>/edit/', views.edit_internship, name='edit_internship'),
    path('internship/<int:pk>/delete/', views.delete_internship, name='delete_internship'),
    path('internship/<int:pk>/toggle-status/', views.toggle_internship_status, name='toggle_status'),
    path('my-internships/', views.my_internships, name='my_internships'),
    
    # Company views - Internship Application management
    path('internship/<int:pk>/applications/', views.view_applications, name='view_applications'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
    path('application/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    
    # User views - Internship
    path('internship/<int:pk>/apply/', views.apply_internship, name='apply_internship'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:pk>/withdraw/', views.withdraw_application, name='withdraw_application'),
    
    # ==================== JOB URLs ====================
    # Public views
    path('jobs/', views.job_list, name='job_list'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    
    # Company views - Job management
    path('jobs/create/', views.create_job, name='create_job'),
    path('job/<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('job/<int:pk>/delete/', views.delete_job, name='delete_job'),
    path('job/<int:pk>/toggle-status/', views.toggle_job_status, name='toggle_job_status'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    
    # Company views - Job Application management
    path('job/<int:pk>/applications/', views.view_job_applications, name='view_job_applications'),
    path('job/<int:pk>/ranked-applicants/', views.ranked_applicants, name='ranked_applicants'),
    path('job-application/<int:pk>/', views.job_application_detail, name='job_application_detail'),
    path('job-application/<int:pk>/update-status/', views.update_job_application_status, name='update_job_application_status'),
    
    # User views - Job
    path('job/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('my-job-applications/', views.my_job_applications, name='my_job_applications'),
    path('job-application/<int:pk>/withdraw/', views.withdraw_job_application, name='withdraw_job_application'),
    
    # ==================== BOOKMARKS ====================
    path('job/<int:pk>/bookmark/', views.toggle_job_bookmark, name='toggle_job_bookmark'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    
    # ==================== RECOMMENDATIONS ====================
    path('recommended-jobs/', views.recommended_jobs, name='recommended_jobs'),
    
    # ==================== ANALYTICS ====================
    path('job/<int:pk>/analytics/', views.job_analytics, name='job_analytics'),
    path('company-analytics/', views.company_dashboard_analytics, name='company_analytics'),
    
    # ==================== INTERVIEWS ====================
    path('job-application/<int:pk>/schedule-interview/', views.schedule_interview, name='schedule_interview'),
    path('interview/<int:pk>/update/', views.update_interview, name='update_interview'),
    path('interview/<int:pk>/cancel/', views.cancel_interview, name='cancel_interview'),
    path('interview/<int:pk>/complete/', views.complete_interview, name='complete_interview'),
    path('my-interviews/', views.my_interviews, name='my_interviews'),
]
