from django.db import models


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=160, default='ForgeCMS')
    tagline = models.CharField(max_length=220, blank=True, default='CMS modulaire prêt pour devenir une CMS Factory')
    default_theme = models.CharField(max_length=120, default='default')
    maintenance_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paramètre du site'
        verbose_name_plural = 'Paramètres du site'

    def __str__(self):
        return self.site_name
