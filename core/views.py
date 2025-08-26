from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Count, Q
from projects.models import Project
from annotations.models import Annotation, AnnotationSession
from .models import UserProfile, Notification
from .forms import CustomUserCreationForm, UserProfileForm

def home(request):
    """Главная страница"""
    if request.user.is_authenticated:
        # Получаем статистику для авторизованного пользователя
        user_projects = Project.objects.filter(
            Q(owner=request.user) | Q(collaborators=request.user)
        )
        
        recent_projects = user_projects.order_by('-created_at')[:5]
        active_projects = user_projects.filter(status='active')
        
        # Статистика аннотаций
        user_annotations = Annotation.objects.filter(annotator=request.user)
        total_annotations = user_annotations.count()
        approved_annotations = user_annotations.filter(status='approved').count()
        
        # Непрочитанные уведомления
        unread_notifications = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        
        context = {
            'recent_projects': recent_projects,
            'active_projects': active_projects,
            'total_annotations': total_annotations,
            'approved_annotations': approved_annotations,
            'unread_notifications': unread_notifications,
        }
    else:
        context = {}
    
    return render(request, 'core/home.html', context)

def register(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(user=user)
            
            # Автоматически входим в систему
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})

@login_required
def dashboard(request):
    """Панель управления пользователя"""
    user = request.user
    
    # Проекты пользователя
    owned_projects = Project.objects.filter(owner=user)
    collaborated_projects = Project.objects.filter(collaborators=user)
    
    # Статистика аннотаций
    annotations = Annotation.objects.filter(annotator=user)
    recent_annotations = annotations.order_by('-created_at')[:10]
    
    # Сессии аннотации
    recent_sessions = AnnotationSession.objects.filter(annotator=user).order_by('-started_at')[:5]
    
    # Уведомления
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:10]
    
    context = {
        'owned_projects': owned_projects,
        'collaborated_projects': collaborated_projects,
        'recent_annotations': recent_annotations,
        'recent_sessions': recent_sessions,
        'notifications': notifications,
        'total_annotations': annotations.count(),
        'approved_annotations': annotations.filter(status='approved').count(),
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def profile(request):
    """Профиль пользователя"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'form': form,
    }
    
    return render(request, 'core/profile.html', context)

@login_required
def notifications(request):
    """Страница уведомлений"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        # Отметить уведомления как прочитанные
        notification_ids = request.POST.getlist('mark_read')
        if notification_ids:
            Notification.objects.filter(
                id__in=notification_ids, user=request.user
            ).update(is_read=True)
            messages.success(request, 'Notifications marked as read!')
            return redirect('notifications')
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'core/notifications.html', context)

@login_required
def statistics(request):
    """Страница статистики"""
    user = request.user
    
    # Статистика проектов
    projects = Project.objects.filter(
        Q(owner=user) | Q(collaborators=user)
    )
    
    # Статистика аннотаций
    annotations = Annotation.objects.filter(annotator=user)
    
    # Статистика по типам проектов
    project_types = projects.values('project_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Статистика по статусам аннотаций
    annotation_statuses = annotations.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Временная статистика (последние 30 дней)
    from django.utils import timezone
    from datetime import timedelta
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_annotations = annotations.filter(created_at__gte=thirty_days_ago)
    
    context = {
        'total_projects': projects.count(),
        'total_annotations': annotations.count(),
        'recent_annotations': recent_annotations.count(),
        'project_types': project_types,
        'annotation_statuses': annotation_statuses,
    }
    
    return render(request, 'core/statistics.html', context)
