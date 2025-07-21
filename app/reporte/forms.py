from django import forms
from .models import ReporteColaborativo


class ReporteColaborativoForm(forms.ModelForm):
    class Meta:
        model = ReporteColaborativo
        exclude = ['usuario_reportador', 'fecha_creacion', 'fecha_actualizacion', 'votos_positivos', 'votos_negativos', 'usuarios_votantes', 'es_validado', 'estado_reporte']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del incidente'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describa lo sucedido'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Venezuela, Cercado'}),
            'tipo_incidente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Robo, incendio...'}),
            'imagen_geolocalizada': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'nivel_peligro': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }


    