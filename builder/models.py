from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .field_types import FIELD_TYPES
from .validators import validate_entry_data


class CustomContentType(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=80, blank=True)
    config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Type de contenu'
        verbose_name_plural = 'Types de contenu'

    def __str__(self):
        return self.name

    def to_schema(self):
        return {
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'config': self.config,
            'fields': [field.to_schema() for field in self.fields.all()],
        }


class CustomField(models.Model):
    content_type = models.ForeignKey(CustomContentType, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    field_type = models.CharField(max_length=40, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    default_value = models.CharField(max_length=255, blank=True)
    help_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['order', 'id']
        unique_together = [('content_type', 'slug')]
        verbose_name = 'Champ personnalisé'
        verbose_name_plural = 'Champs personnalisés'

    def __str__(self):
        return f'{self.content_type.name} / {self.name}'

    def to_schema(self):
        return {
            'name': self.name,
            'slug': self.slug,
            'type': self.field_type,
            'required': self.required,
            'unique': self.unique,
            'default': self.default_value,
            'config': self.config,
        }


class CustomEntry(models.Model):
    content_type = models.ForeignKey(CustomContentType, on_delete=models.CASCADE, related_name='entries')
    data = models.JSONField(default=dict)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Entrée personnalisée'
        verbose_name_plural = 'Entrées personnalisées'

    def __str__(self):
        return f'{self.content_type.name} #{self.id}'

    def clean(self):
        super().clean()
        if not self.content_type_id:
            return

        errors = validate_entry_data(self.content_type, self.data, instance=self)
        if errors:
            messages = [f'{slug}: {message}' for slug, message in errors.items()]
            raise ValidationError({'data': messages})

    def save(self, *args, **kwargs):
        # Django ne lance pas full_clean() automatiquement sur Model.save().
        # L'imposer ici protège aussi les futures API, commandes et plugins.
        self.full_clean()
        return super().save(*args, **kwargs)


class BuilderSnapshot(models.Model):
    name = models.CharField(max_length=160)
    note = models.CharField(max_length=255, blank=True)
    schema = models.JSONField(default=dict)
    is_auto = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='builder_snapshots',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Snapshot builder'
        verbose_name_plural = 'Snapshots builder'

    def __str__(self):
        return self.name
