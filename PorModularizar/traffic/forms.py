from django import forms
from django.core.exceptions import ValidationError
from .models import TrafficIncident
import PIL.Image

MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5MB
MIN_DESCRIPTION_LENGTH = 10  # los caracteres mínimos para la descripción
MIN_IMAGE_DIMENSION = 100  # dimensiones mínimas de la imagen


class TrafficIncidentForm(forms.ModelForm):
    class Meta:
        model = TrafficIncident
        fields = ['title', 'description', 'incident_type', 'photo', 'latitude', 'longitude']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Accidente en Av. Principal'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el incidente en detalle...'
            }),
            'incident_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def clean_photo(self):
        """Validación específica para fotos"""
        photo = self.cleaned_data.get('photo')
        
        if photo:
            # Validar tamaño del archivo
            if photo.size > MAX_PHOTO_SIZE:
                raise ValidationError('La imagen no puede ser mayor a 5MB')
            
            # Validar que sea una imagen válida
            try:
                img = PIL.Image.open(photo)
                img.verify()
            except Exception:
                raise ValidationError('El archivo no es una imagen válida')
            
            # Validar dimensiones mínimas
            photo.seek(0)  # Reset file pointer
            img = PIL.Image.open(photo)
            width, height = img.size

            if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                raise ValidationError(f'La imagen debe tener al menos {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION} píxeles')

        return photo

    def clean_description(self):
        """Validación específica para descripción"""
        description = self.cleaned_data.get('description')
        
        if description:
            # Remover espacios extra
            description = description.strip()
            
            # Validar longitud mínima
            if len(description) < MIN_DESCRIPTION_LENGTH:
                raise ValidationError(f'La descripción debe tener al menos {MIN_DESCRIPTION_LENGTH} caracteres')

            # Validar que no sea solo números o caracteres especiales
            if not any(c.isalpha() for c in description):
                raise ValidationError('La descripción debe contener texto descriptivo')
        
        return description

    def clean(self):
        """Validaciones que involucran múltiples campos"""
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')
        
        # Validar que se hayan proporcionado coordenadas
        if not lat or not lng:
            raise ValidationError('Debe seleccionar una ubicación en el mapa')
        
        return cleaned_data