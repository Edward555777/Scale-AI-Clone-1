from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

def project_file_path(instance, filename):
    """Путь для файлов проекта"""
    return f'projects/{instance.project.id}/{filename}'

class Project(models.Model):
    """Проект для аннотации данных"""
    PROJECT_TYPES = [
        ('image_classification', 'Image Classification'),
        ('object_detection', 'Object Detection'),
        ('semantic_segmentation', 'Semantic Segmentation'),
        ('text_classification', 'Text Classification'),
        ('named_entity_recognition', 'Named Entity Recognition'),
        ('sentiment_analysis', 'Sentiment Analysis'),
        ('custom', 'Custom'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=30, choices=PROJECT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Владелец и участники
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    collaborators = models.ManyToManyField(User, related_name='collaborated_projects', blank=True)
    
    # Настройки проекта
    instructions = models.TextField(blank=True)
    guidelines = models.TextField(blank=True)
    
    # Статистика
    total_files = models.IntegerField(default=0)
    annotated_files = models.IntegerField(default=0)
    quality_score = models.FloatField(default=0.0)
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_progress_percentage(self):
        """Получить процент выполнения проекта"""
        if self.total_files == 0:
            return 0
        return (self.annotated_files / self.total_files) * 100

class ProjectFile(models.Model):
    """Файл в проекте"""
    FILE_TYPES = [
        ('image', 'Image'),
        ('text', 'Text'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=project_file_path)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    
    # Статус аннотации
    is_annotated = models.BooleanField(default=False)
    annotation_count = models.IntegerField(default=0)
    
    # Метаданные
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - {self.project.name}"
    
    def save(self, *args, **kwargs):
        if not self.filename:
            self.filename = os.path.basename(self.file.name)
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

class ProjectSettings(models.Model):
    """Настройки проекта"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='settings')
    
    # Настройки аннотации
    require_quality_check = models.BooleanField(default=True)
    min_annotations_per_file = models.IntegerField(default=1)
    max_annotations_per_file = models.IntegerField(default=3)
    
    # Настройки качества
    quality_threshold = models.FloatField(default=0.8)
    auto_approve_threshold = models.FloatField(default=0.95)
    
    # Настройки экспорта
    export_format = models.CharField(max_length=20, default='json')
    include_metadata = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.project.name}"
