from django import forms
from . import models


class VehiculeForm(forms.ModelForm):
    class Meta:
        model = models.Vehicule
        fields = '__all__'
