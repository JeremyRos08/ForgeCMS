from django.contrib import admin
from . import models


@admin.register(models.Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('id', 'marque', 'modele', 'immatriculation', 'updated_at')
    search_fields = ('marque', 'modele', 'immatriculation')
