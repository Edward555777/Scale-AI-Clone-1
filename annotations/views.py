from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Annotation, AnnotationTemplate, QualityReview, AnnotationLabel, AnnotationSession
from projects.models import Project, ProjectFile
from django.utils import timezone

@login_required
def annotation_list(request):
    """Список аннотаций пользователя"""
    user = request.user
    
    # Получаем аннотации пользователя
    annotations = Annotation.objects.filter(annotator=user).order_by('-created_at')
    
    # Фильтрация
    status_filter = request.GET.get('status')
    if status_filter:
        annotations = annotations.filter(status=status_filter)
    
    project_filter = request.GET.get('project')
    if project_filter:
        annotations = annotations.filter(project_id=project_filter)
    
    # Поиск
    search_query = request.GET.get('search')
    if search_query:
        annotations = annotations.filter(
            Q(file__filename__icontains=search_query) |
            Q(annotator_notes__icontains=search_query)
        )
    
    # Пагинация
    paginator = Paginator(annotations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Проекты для фильтра
    user_projects = Project.objects.filter(
        Q(owner=user) | Q(collaborators=user)
    )
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'search_query': search_query,
        'user_projects': user_projects,
        'total_annotations': annotations.count(),
    }
    
    return render(request, 'annotations/annotation_list.html', context)

@login_required
def annotation_create(request):
    """Создание новой аннотации"""
    # Получаем доступные файлы для аннотации
    user_projects = Project.objects.filter(
        Q(owner=request.user) | Q(collaborators=request.user)
    ).filter(status='active')
    
    if request.method == 'POST':
        project_id = request.POST.get('project')
        file_id = request.POST.get('file')
        
        if project_id and file_id:
            project = get_object_or_404(Project, id=project_id)
            project_file = get_object_or_404(ProjectFile, id=file_id, project=project)
            
            # Проверяем, не аннотировал ли уже пользователь этот файл
            existing_annotation = Annotation.objects.filter(
                annotator=request.user,
                file=project_file
            ).first()
            
            if existing_annotation:
                messages.warning(request, 'You have already annotated this file.')
                return redirect('annotations:annotation_edit', pk=existing_annotation.pk)
            
            # Создаем новую аннотацию
            annotation = Annotation.objects.create(
                project=project,
                file=project_file,
                annotator=request.user,
                annotation_data={},
                status='draft'
            )
            
            messages.success(request, 'Annotation created successfully!')
            return redirect('annotations:annotation_edit', pk=annotation.pk)
        else:
            messages.error(request, 'Please select a project and file.')
    
    context = {
        'user_projects': user_projects,
    }
    
    return render(request, 'annotations/annotation_create.html', context)

@login_required
def annotation_detail(request, pk):
    """Детальная информация об аннотации"""
    annotation = get_object_or_404(Annotation, pk=pk)
    
    # Проверяем права доступа
    if annotation.annotator != request.user and annotation.project.owner != request.user:
        messages.error(request, 'You do not have permission to view this annotation.')
        return redirect('annotations:annotation_list')
    
    # Получаем обзоры качества
    quality_reviews = annotation.quality_reviews.all()
    
    context = {
        'annotation': annotation,
        'quality_reviews': quality_reviews,
    }
    
    return render(request, 'annotations/annotation_detail.html', context)

@login_required
def annotation_edit(request, pk):
    """Редактирование аннотации"""
    annotation = get_object_or_404(Annotation, pk=pk)
    
    # Проверяем права доступа
    if annotation.annotator != request.user:
        messages.error(request, 'You do not have permission to edit this annotation.')
        return redirect('annotations:annotation_detail', pk=annotation.pk)
    
    if request.method == 'POST':
        # Обработка данных аннотации
        annotation_data = {}
        
        # В зависимости от типа проекта обрабатываем разные данные
        if annotation.project.project_type == 'image_classification':
            annotation_data['label'] = request.POST.get('label')
            annotation_data['confidence'] = float(request.POST.get('confidence', 1.0))
        
        elif annotation.project.project_type == 'object_detection':
            # Здесь будет обработка bounding boxes
            annotation_data['objects'] = []
            # Пока просто сохраняем пустой список
        
        elif annotation.project.project_type == 'text_classification':
            annotation_data['label'] = request.POST.get('label')
            annotation_data['confidence'] = float(request.POST.get('confidence', 1.0))
        
        # Обновляем аннотацию
        annotation.annotation_data = annotation_data
        annotation.annotator_notes = request.POST.get('annotator_notes', '')
        
        # Если пользователь отправил аннотацию
        if 'submit' in request.POST:
            annotation.status = 'submitted'
            annotation.submitted_at = timezone.now()
            messages.success(request, 'Annotation submitted successfully!')
        else:
            annotation.status = 'draft'
            messages.success(request, 'Annotation saved as draft!')
        
        annotation.save()
        return redirect('annotations:annotation_detail', pk=annotation.pk)
    
    # Получаем метки для проекта
    labels = annotation.project.labels.filter(is_active=True)
    
    context = {
        'annotation': annotation,
        'labels': labels,
    }
    
    return render(request, 'annotations/annotation_edit.html', context)

@login_required
def annotation_delete(request, pk):
    """Удаление аннотации"""
    annotation = get_object_or_404(Annotation, pk=pk)
    
    # Проверяем права доступа
    if annotation.annotator != request.user:
        messages.error(request, 'You do not have permission to delete this annotation.')
        return redirect('annotations:annotation_detail', pk=annotation.pk)
    
    if request.method == 'POST':
        annotation.delete()
        messages.success(request, 'Annotation deleted successfully!')
        return redirect('annotations:annotation_list')
    
    context = {
        'annotation': annotation,
    }
    
    return render(request, 'annotations/annotation_confirm_delete.html', context)

@login_required
def quality_review(request):
    """Страница обзора качества"""
    user = request.user
    
    # Получаем аннотации для обзора
    # Показываем только аннотации из проектов, где пользователь является владельцем
    annotations_for_review = Annotation.objects.filter(
        project__owner=user,
        status='submitted'
    ).order_by('-submitted_at')
    
    # Фильтрация
    project_filter = request.GET.get('project')
    if project_filter:
        annotations_for_review = annotations_for_review.filter(project_id=project_filter)
    
    # Пагинация
    paginator = Paginator(annotations_for_review, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Проекты для фильтра
    user_projects = Project.objects.filter(owner=user)
    
    context = {
        'page_obj': page_obj,
        'project_filter': project_filter,
        'user_projects': user_projects,
    }
    
    return render(request, 'annotations/quality_review.html', context)

@login_required
def template_list(request):
    """Список шаблонов аннотаций"""
    user = request.user
    
    # Получаем шаблоны из проектов пользователя
    templates = AnnotationTemplate.objects.filter(
        project__owner=user
    ).order_by('-created_at')
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'annotations/template_list.html', context)

@login_required
def template_create(request):
    """Создание шаблона аннотации"""
    user = request.user
    
    # Получаем проекты пользователя
    user_projects = Project.objects.filter(owner=user)
    
    if request.method == 'POST':
        project_id = request.POST.get('project')
        name = request.POST.get('name')
        description = request.POST.get('description')
        schema = request.POST.get('schema', '{}')
        
        if project_id and name:
            project = get_object_or_404(Project, id=project_id, owner=user)
            
            # Создаем шаблон
            template = AnnotationTemplate.objects.create(
                project=project,
                name=name,
                description=description,
                schema=schema
            )
            
            messages.success(request, 'Template created successfully!')
            return redirect('annotations:template_list')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'user_projects': user_projects,
    }
    
    return render(request, 'annotations/template_form.html', context)

@login_required
def label_list(request):
    """Список меток"""
    user = request.user
    
    # Получаем метки из проектов пользователя
    labels = AnnotationLabel.objects.filter(
        project__owner=user
    ).order_by('project__name', 'name')
    
    context = {
        'labels': labels,
    }
    
    return render(request, 'annotations/label_list.html', context)

@login_required
def label_create(request):
    """Создание метки"""
    user = request.user
    
    # Получаем проекты пользователя
    user_projects = Project.objects.filter(owner=user)
    
    if request.method == 'POST':
        project_id = request.POST.get('project')
        name = request.POST.get('name')
        description = request.POST.get('description')
        color = request.POST.get('color', '#007bff')
        
        if project_id and name:
            project = get_object_or_404(Project, id=project_id, owner=user)
            
            # Создаем метку
            label = AnnotationLabel.objects.create(
                project=project,
                name=name,
                description=description,
                color=color
            )
            
            messages.success(request, 'Label created successfully!')
            return redirect('annotations:label_list')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'user_projects': user_projects,
    }
    
    return render(request, 'annotations/label_form.html', context)

@login_required
def session_list(request):
    """Список сессий аннотации"""
    user = request.user
    
    # Получаем сессии пользователя
    sessions = AnnotationSession.objects.filter(annotator=user).order_by('-started_at')
    
    # Пагинация
    paginator = Paginator(sessions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_sessions': sessions.count(),
    }
    
    return render(request, 'annotations/session_list.html', context)
