"""
URL configuration for scale_ai_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from demo_views import demo_home, demo_projects, demo_project_detail, demo_annotation_tool, demo_create_project, demo_upload_file, demo_export_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', demo_home, name='demo_home'),
    path('projects/', demo_projects, name='demo_projects'),
    path('projects/<int:project_id>/', demo_project_detail, name='demo_project_detail'),
    path('annotation-tool/', demo_annotation_tool, name='demo_annotation_tool'),
    path('demo/create-project/', demo_create_project, name='demo_create_project'),
    path('demo/upload-file/', demo_upload_file, name='demo_upload_file'),
    path('demo/export-data/', demo_export_data, name='demo_export_data'),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Добавляем маршруты для медиа файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
