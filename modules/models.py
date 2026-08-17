from django.db import models


class InstalledModule(models.Model):
    name = models.CharField(max_length=120, unique=True)
    label = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)
    version = models.CharField(max_length=40, default='1.0.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['label']
        verbose_name = 'Module installé'
        verbose_name_plural = 'Modules installés'

    def __str__(self):
        return self.label
