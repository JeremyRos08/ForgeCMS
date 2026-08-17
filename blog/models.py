from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=160, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=220, unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})
