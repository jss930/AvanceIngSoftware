from django import forms
from django.contrib.auth.models import User
from .models import Alerta

class AlertaForm(forms.ModelForm):
    destinatarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    fecha_expiracion = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'  # Muy importante este formato
        )
    )

    class Meta:
        model = Alerta
        fields = ['titulo', 'mensaje', 'destinatarios', 'ubicacion', 'prioridad', 'activo', 'fecha_expiracion']
