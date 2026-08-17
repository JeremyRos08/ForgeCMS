from django.db import models


class Vehicule(models.Model):
    marque = models.CharField(max_length=255)
    modele = models.CharField(max_length=255)
    immatriculation = models.CharField(max_length=255, blank=True)
    date_entretien = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Véhicule'
        verbose_name_plural = 'Véhicules'
        ordering = ['-id']

    def __str__(self):
        return str(self.marque)
