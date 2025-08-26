from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Project, ProjectFile, ProjectSettings
from .forms import ProjectForm, ProjectFileForm

@login_required
def project_list(request):
    """Список проектов пользователя"""
    user = request.user
    
    # Получаем проекты пользователя
    projects = Project.objects.filter(
        Q(owner=user) | Q(collaborators=user)
    ).order_by('-created_at')
    
    # Фильтрация
    status_filter = request.GET.get('status')
    if status_filter:
        projects = projects.filter(status=status_filter)
    
    # Поиск
    search_query = request.GET.get('search')
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Пагинация
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_projects': projects.count(),
    }
    
    return render(request, 'projects/project_list.html', context)

@login_required
def project_create(request):
    """Создание нового проекта"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            
            # Создаем настройки проекта по умолчанию
            ProjectSettings.objects.create(project=project)
            
            messages.success(request, 'Project created successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'title': 'Create New Project',
    }
    
    return render(request, 'projects/project_form.html', context)

@login_required
def project_detail(request, pk):
    """Детальная информация о проекте"""
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем права доступа
    if project.owner != request.user and request.user not in project.collaborators.all():
        messages.error(request, 'You do not have permission to view this project.')
        return redirect('projects:project_list')
    
    # Статистика проекта
    total_files = project.files.count()
    annotated_files = project.files.filter(is_annotated=True).count()
    progress_percentage = (annotated_files / total_files * 100) if total_files > 0 else 0
    
    # Последние файлы
    recent_files = project.files.order_by('-uploaded_at')[:5]
    
    # Последние аннотации
    recent_annotations = project.annotations.order_by('-created_at')[:5]
    
    context = {
        'project': project,
        'total_files': total_files,
        'annotated_files': annotated_files,
        'progress_percentage': progress_percentage,
        'recent_files': recent_files,
        'recent_annotations': recent_annotations,
    }
    
    return render(request, 'projects/project_detail.html', context)

@login_required
def project_edit(request, pk):
    """Редактирование проекта"""
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем права доступа
    if project.owner != request.user:
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('projects:project_detail', pk=project.pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'title': 'Edit Project',
    }
    
    return render(request, 'projects/project_form.html', context)

@login_required
def project_delete(request, pk):
    """Удаление проекта"""
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем права доступа
    if project.owner != request.user:
        messages.error(request, 'You do not have permission to delete this project.')
        return redirect('projects:project_detail', pk=project.pk)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('projects:project_list')
    
    context = {
        'project': project,
    }
    
    return render(request, 'projects/project_confirm_delete.html', context)

@login_required
def project_files(request, pk):
    """Список файлов проекта"""
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем права доступа
    if project.owner != request.user and request.user not in project.collaborators.all():
        messages.error(request, 'You do not have permission to view this project.')
        return redirect('projects:project_list')
    
    files = project.files.all()
    
    # Фильтрация
    file_type = request.GET.get('type')
    if file_type:
        files = files.filter(file_type=file_type)
    
    # Поиск
    search_query = request.GET.get('search')
    if search_query:
        files = files.filter(filename__icontains=search_query)
    
    # Пагинация
    paginator = Paginator(files, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'project': project,
        'page_obj': page_obj,
        'file_type': file_type,
        'search_query': search_query,
    }
    
    return render(request, 'projects/project_files.html', context)

@login_required
def file_upload(request, pk):
    """Загрузка файлов в проект"""
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем права доступа
    if project.owner != request.user and request.user not in project.collaborators.all():
        messages.error(request, 'You do not have permission to upload files to this project.')
        return redirect('projects:project_detail', pk=project.pk)
    
    if request.method == 'POST':
        form = ProjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('file')
            
            for uploaded_file in files:
                project_file = form.save(commit=False)
                project_file.project = project
                project_file.file = uploaded_file
                project_file.uploaded_by = request.user
                project_file.save()
            
            messages.success(request, f'{len(files)} file(s) uploaded successfully!')
            return redirect('projects:project_files', pk=project.pk)
    else:
        form = ProjectFileForm()
    
    context = {
        'form': form,
        'project': project,
    }
    
    return render(request, 'projects/file_upload.html', context)

@login_required
def project_settings(request, pk):
    """Настройки проекта"""
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем права доступа
    if project.owner != request.user:
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('projects:project_detail', pk=project.pk)
    
    try:
        settings = project.settings
    except ProjectSettings.DoesNotExist:
        settings = ProjectSettings.objects.create(project=project)
    
    if request.method == 'POST':
        # Обновление настроек
        settings.require_quality_check = request.POST.get('require_quality_check') == 'on'
        settings.min_annotations_per_file = int(request.POST.get('min_annotations_per_file', 1))
        settings.max_annotations_per_file = int(request.POST.get('max_annotations_per_file', 3))
        settings.quality_threshold = float(request.POST.get('quality_threshold', 0.8))
        settings.auto_approve_threshold = float(request.POST.get('auto_approve_threshold', 0.95))
        settings.export_format = request.POST.get('export_format', 'json')
        settings.include_metadata = request.POST.get('include_metadata') == 'on'
        settings.save()
        
        messages.success(request, 'Project settings updated successfully!')
        return redirect('projects:project_settings', pk=project.pk)
    
    context = {
        'project': project,
        'settings': settings,
    }
    
    return render(request, 'projects/project_settings.html', context)

@login_required
def project_export(request, pk):
    """Экспорт данных проекта"""
    project = get_object_or_404(Project, pk=pk)
    
    # Проверяем права доступа
    if project.owner != request.user and request.user not in project.collaborators.all():
        messages.error(request, 'You do not have permission to export this project.')
        return redirect('projects:project_detail', pk=project.pk)
    
    # Здесь будет логика экспорта данных
    # Пока просто возвращаем сообщение
    messages.info(request, 'Export functionality will be implemented in the next phase.')
    return redirect('projects:project_detail', pk=project.pk)
