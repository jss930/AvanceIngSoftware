from django import forms
from django.contrib.auth.models import User
from app.reporte.models import Alerta

FORM_CONTROL = 'form-control'

class AlertaForm(forms.ModelForm):
    destinatarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'id': 'destinatarios',
        }),
        required=False,
    )

    class Meta:
        model = Alerta
        fields = ['titulo', 'mensaje', 'destinatarios', 'ubicacion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': FORM_CONTROL}),
            'mensaje': forms.Textarea(attrs={'class': FORM_CONTROL}),
            'ubicacion': forms.TextInput(attrs={'class': FORM_CONTROL}),
        }

