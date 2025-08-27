from django import forms
from .models import Project, ProjectFile

class ProjectForm(forms.ModelForm):
    """Форма для создания и редактирования проекта"""
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'project_type', 'status', 'visibility', 'instructions', 'guidelines', 'deadline']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your project'
            }),
            'project_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-select'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Provide detailed instructions for annotators'
            }),
            'guidelines': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Add annotation guidelines and best practices'
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем CSS классы для всех полей
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

class ProjectFileForm(forms.ModelForm):
    """Форма для загрузки файлов в проект"""
    
    class Meta:
        model = ProjectFile
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.txt,.csv,.json,.xml,.pdf,.doc,.docx'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = True
        self.fields['file'].help_text = 'Select one or more files to upload. Supported formats: images, text, CSV, JSON, XML, PDF, DOC.'
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Проверяем размер файла (10MB максимум)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 10MB.')
            
            # Проверяем расширение файла
            allowed_extensions = [
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',  # Изображения
                '.txt', '.csv', '.json', '.xml',  # Текстовые файлы
                '.pdf', '.doc', '.docx'  # Документы
            ]
            
            import os
            file_extension = os.path.splitext(file.name)[1].lower()
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f'File type {file_extension} is not supported. '
                    f'Allowed types: {", ".join(allowed_extensions)}'
                )
        
        return file

class ProjectSettingsForm(forms.ModelForm):
    """Форма для настроек проекта"""
    
    class Meta:
        model = Project
        fields = []  # Пустой список, так как настройки хранятся в отдельной модели
    
    # Настройки аннотации
    require_quality_check = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Require quality review for all annotations'
    )
    
    min_annotations_per_file = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Minimum number of annotations required per file'
    )
    
    max_annotations_per_file = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=3,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Maximum number of annotations allowed per file'
    )
    
    # Настройки качества
    quality_threshold = forms.FloatField(
        min_value=0.0,
        max_value=1.0,
        initial=0.8,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text='Minimum quality score required for approval (0.0 - 1.0)'
    )
    
    auto_approve_threshold = forms.FloatField(
        min_value=0.0,
        max_value=1.0,
        initial=0.95,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text='Quality score above which annotations are automatically approved'
    )
    
    # Настройки экспорта
    export_format = forms.ChoiceField(
        choices=[
            ('json', 'JSON'),
            ('csv', 'CSV'),
            ('xml', 'XML'),
            ('yolo', 'YOLO'),
            ('coco', 'COCO'),
        ],
        initial='json',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Default format for exporting annotations'
    )
    
    include_metadata = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Include metadata in exported files'
    )
    
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        
        if project and hasattr(project, 'settings'):
            settings = project.settings
            self.fields['require_quality_check'].initial = settings.require_quality_check
            self.fields['min_annotations_per_file'].initial = settings.min_annotations_per_file
            self.fields['max_annotations_per_file'].initial = settings.max_annotations_per_file
            self.fields['quality_threshold'].initial = settings.quality_threshold
            self.fields['auto_approve_threshold'].initial = settings.auto_approve_threshold
            self.fields['export_format'].initial = settings.export_format
            self.fields['include_metadata'].initial = settings.include_metadata

class ProjectCollaboratorForm(forms.Form):
    """Форма для добавления участников в проект"""
    
    collaborator_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter collaborator email'
        }),
        help_text='Enter the email address of the person you want to invite'
    )
    
    role = forms.ChoiceField(
        choices=[
            ('annotator', 'Annotator'),
            ('reviewer', 'Reviewer'),
            ('admin', 'Administrator'),
        ],
        initial='annotator',
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Select the role for this collaborator'
    )
    
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional message for the invitation'
        }),
        help_text='Optional message to include with the invitation'
    )
