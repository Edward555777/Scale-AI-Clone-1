from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('<int:pk>/files/', views.project_files, name='project_files'),
    path('<int:pk>/files/upload/', views.file_upload, name='file_upload'),
    path('<int:pk>/settings/', views.project_settings, name='project_settings'),
    path('<int:pk>/export/', views.project_export, name='project_export'),
]
