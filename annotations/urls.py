from django.urls import path
from . import views

app_name = 'annotations'

urlpatterns = [
    path('', views.annotation_list, name='annotation_list'),
    path('create/', views.annotation_create, name='annotation_create'),
    path('<int:pk>/', views.annotation_detail, name='annotation_detail'),
    path('<int:pk>/edit/', views.annotation_edit, name='annotation_edit'),
    path('<int:pk>/delete/', views.annotation_delete, name='annotation_delete'),
    path('review/', views.quality_review, name='quality_review'),
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('labels/', views.label_list, name='label_list'),
    path('labels/create/', views.label_create, name='label_create'),
    path('sessions/', views.session_list, name='session_list'),
]
