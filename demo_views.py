from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from datetime import datetime

# Демо-данные
DEMO_PROJECTS = [
    {
        'id': 1,
        'name': 'Image Classification Demo',
        'description': 'Classify images into categories like animals, vehicles, food',
        'type': 'Image Classification',
        'status': 'Active',
        'progress': 75,
        'files_count': 50,
        'annotated_count': 38,
        'created_at': '2025-08-27'
    },
    {
        'id': 2,
        'name': 'Text Sentiment Analysis',
        'description': 'Analyze sentiment in customer reviews and feedback',
        'type': 'Sentiment Analysis',
        'status': 'Active',
        'progress': 45,
        'files_count': 100,
        'annotated_count': 45,
        'created_at': '2025-08-26'
    },
    {
        'id': 3,
        'name': 'Object Detection Project',
        'description': 'Detect objects in street scene images',
        'type': 'Object Detection',
        'status': 'Completed',
        'progress': 100,
        'files_count': 200,
        'annotated_count': 200,
        'created_at': '2025-08-25'
    }
]

DEMO_FILES = [
    {'id': 1, 'name': 'cat_image_001.jpg', 'type': 'Image', 'size': '2.3 MB', 'status': 'Annotated'},
    {'id': 2, 'name': 'dog_image_002.jpg', 'type': 'Image', 'size': '1.8 MB', 'status': 'Annotated'},
    {'id': 3, 'name': 'review_001.txt', 'type': 'Text', 'size': '1.2 KB', 'status': 'Pending'},
    {'id': 4, 'name': 'review_002.txt', 'type': 'Text', 'size': '0.8 KB', 'status': 'Annotated'},
    {'id': 5, 'name': 'street_scene_001.jpg', 'type': 'Image', 'size': '3.1 MB', 'status': 'Annotated'},
]

def demo_home(request):
    """Демо главная страница"""
    context = {
        'total_projects': len(DEMO_PROJECTS),
        'total_files': sum(p['files_count'] for p in DEMO_PROJECTS),
        'total_annotations': sum(p['annotated_count'] for p in DEMO_PROJECTS),
        'recent_projects': DEMO_PROJECTS[:3],
        'is_demo': True
    }
    return render(request, 'demo/home.html', context)

def demo_projects(request):
    """Демо список проектов"""
    context = {
        'projects': DEMO_PROJECTS,
        'is_demo': True
    }
    return render(request, 'demo/projects.html', context)

def demo_project_detail(request, project_id):
    """Демо детали проекта"""
    project = next((p for p in DEMO_PROJECTS if p['id'] == project_id), None)
    if not project:
        return render(request, 'demo/404.html', {'is_demo': True})
    
    context = {
        'project': project,
        'files': DEMO_FILES,
        'is_demo': True
    }
    return render(request, 'demo/project_detail.html', context)

def demo_annotation_tool(request):
    """Демо инструмент аннотации"""
    context = {
        'is_demo': True,
        'annotation_types': [
            'Image Classification',
            'Object Detection', 
            'Text Classification',
            'Sentiment Analysis',
            'Named Entity Recognition'
        ]
    }
    return render(request, 'demo/annotation_tool.html', context)

@csrf_exempt
def demo_create_project(request):
    """Демо создание проекта"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_project = {
                'id': len(DEMO_PROJECTS) + 1,
                'name': data.get('name', 'New Project'),
                'description': data.get('description', ''),
                'type': data.get('type', 'Custom'),
                'status': 'Active',
                'progress': 0,
                'files_count': 0,
                'annotated_count': 0,
                'created_at': datetime.now().strftime('%Y-%m-%d')
            }
            DEMO_PROJECTS.append(new_project)
            return JsonResponse({'success': True, 'project': new_project})
        except:
            return JsonResponse({'success': False, 'error': 'Invalid data'})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

def demo_upload_file(request):
    """Демо загрузка файла"""
    if request.method == 'POST':
        # Симуляция загрузки файла
        return JsonResponse({
            'success': True, 
            'message': 'File uploaded successfully!',
            'file_id': len(DEMO_FILES) + 1
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})

def demo_export_data(request):
    """Демо экспорт данных"""
    return JsonResponse({
        'success': True,
        'message': 'Data exported successfully!',
        'download_url': '#demo-export'
    })
