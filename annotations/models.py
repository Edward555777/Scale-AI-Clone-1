from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from projects.models import Project, ProjectFile
import json

class Annotation(models.Model):
    """Базовая модель аннотации"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('needs_review', 'Needs Review'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='annotations')
    file = models.ForeignKey(ProjectFile, on_delete=models.CASCADE, related_name='annotations')
    annotator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annotations')
    
    # Данные аннотации (хранится как JSON)
    annotation_data = models.JSONField()
    
    # Статус и качество
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    quality_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        null=True, blank=True
    )
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviewed_annotations'
    )
    
    # Комментарии
    annotator_notes = models.TextField(blank=True)
    reviewer_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['file', 'annotator']
    
    def __str__(self):
        return f"Annotation by {self.annotator.username} on {self.file.filename}"
    
    def get_annotation_summary(self):
        """Получить краткое описание аннотации"""
        if self.project.project_type == 'image_classification':
            return f"Classified as: {self.annotation_data.get('label', 'Unknown')}"
        elif self.project.project_type == 'object_detection':
            objects = self.annotation_data.get('objects', [])
            return f"Detected {len(objects)} objects"
        elif self.project.project_type == 'text_classification':
            return f"Classified as: {self.annotation_data.get('label', 'Unknown')}"
        return "Annotation completed"

class AnnotationTemplate(models.Model):
    """Шаблон аннотации для проекта"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='annotation_templates')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Схема аннотации (JSON Schema)
    schema = models.JSONField()
    
    # Настройки шаблона
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"

class QualityReview(models.Model):
    """Обзор качества аннотации"""
    REVIEW_TYPES = [
        ('manual', 'Manual Review'),
        ('automatic', 'Automatic Review'),
        ('peer', 'Peer Review'),
    ]
    
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, related_name='quality_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quality_reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES)
    
    # Оценка качества
    accuracy_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    completeness_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    consistency_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Общая оценка
    overall_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Комментарии
    comments = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    
    # Решение
    is_approved = models.BooleanField(default=False)
    needs_revision = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quality review by {self.reviewer.username} on {self.annotation}"
    
    def save(self, *args, **kwargs):
        # Автоматически вычисляем общую оценку
        self.overall_score = (
            self.accuracy_score + 
            self.completeness_score + 
            self.consistency_score
        ) / 3
        super().save(*args, **kwargs)

class AnnotationLabel(models.Model):
    """Метки для аннотаций"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='labels')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff')  # HEX color
    is_active = models.BooleanField(default=True)
    
    # Для иерархических меток
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['project', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"

class AnnotationSession(models.Model):
    """Сессия аннотации"""
    annotator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annotation_sessions')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='annotation_sessions')
    
    # Статистика сессии
    files_annotated = models.IntegerField(default=0)
    total_time_minutes = models.IntegerField(default=0)
    
    # Временные метки
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Метаданные
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"Session by {self.annotator.username} on {self.project.name}"
    
    def get_duration_minutes(self):
        """Получить продолжительность сессии в минутах"""
        if self.ended_at:
            duration = self.ended_at - self.started_at
            return int(duration.total_seconds() / 60)
        return 0
