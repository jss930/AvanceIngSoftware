from django import forms
from .models import ReporteColaborativo

class ReporteColaborativoForm(forms.ModelForm):
    class Meta:
        model = ReporteColaborativo
        fields = [
            'titulo',
            'descripcion',
            'ubicacion',
            'tipo_incidente',
            'imagen_geolocalizada',
            'nivel_peligro',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del incidente'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describa lo sucedido'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Av. Venezuela, Arequipa',
                'id': 'id_ubicacion',
                'name': 'ubicacion'
            }),
            'tipo_incidente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Robo, incendio...'
            }),
            'imagen_geolocalizada': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'nivel_peligro': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5
            }),
        }
