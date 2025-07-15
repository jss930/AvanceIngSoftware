# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

FORM_CONTROL = 'form-control'
FORM_CONTROL_PASSWORD_INPUT = 'form-control password-input'

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': FORM_CONTROL,
        'placeholder': 'Correo electrónico',
        'id': 'email',
    }))
   
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': FORM_CONTROL,
        'placeholder': 'Usuario',
        'id': 'username',
    }))
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': FORM_CONTROL_PASSWORD_INPUT,
        'placeholder': 'Contraseña',
        'id': 'password1',
    }))
   
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': FORM_CONTROL_PASSWORD_INPUT,
        'placeholder': 'Confirmar contraseña',
        'id': 'password2',
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Nuevo formulario de login
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': FORM_CONTROL,
        'placeholder': 'Usuario o correo electrónico',
        'id': 'username',
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': FORM_CONTROL_PASSWORD_INPUT,
        'placeholder': 'Contraseña',
        'id': 'password',
    }))



# haber 
from django import forms
from django.core.exceptions import ValidationError
from .models import TrafficIncident
import PIL.Image
import os

MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5MB
MIN_DESCRIPTION_LENGTH = 10  # los caracteres mínimos para la descripción
MIN_IMAGE_DIMENSION = 100  # dimensiones mínimas de la imagen
ALLOWED_IMAGE_TYPES = ['JPEG', 'PNG', 'GIF', 'WEBP']


class TrafficIncidentForm(forms.ModelForm):
    class Meta:
        model = TrafficIncident
        fields = ['title', 'description', 'incident_type', 'photo', 'latitude', 'longitude']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Accidente en Av. Principal',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el incidente en detalle...',
                'maxlength': 1000
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

    def clean_title(self):
        """Validación específica para el título"""
        title = self.cleaned_data.get('title')
        
        if title:
            title = title.strip()
            
            # Validar longitud mínima
            if len(title) < 5:
                raise ValidationError('El título debe tener al menos 5 caracteres')
            
            # Validar que no sea solo números o caracteres especiales
            if not any(c.isalpha() for c in title):
                raise ValidationError('El título debe contener texto descriptivo')
                
            # Validar que no sean solo mayúsculas (excepto si es muy corto)
            if len(title) > 10 and title.isupper():
                raise ValidationError('Evita escribir todo en mayúsculas')
        
        return title

    def clean_photo(self):
        """Validación específica para fotos"""
        photo = self.cleaned_data.get('photo')
        
        if photo:
            # Validar tamaño del archivo
            if photo.size > MAX_PHOTO_SIZE:
                raise ValidationError('La imagen no puede ser mayor a 5MB')
            
            # Validar extensión del archivo
            file_ext = os.path.splitext(photo.name)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                raise ValidationError('Solo se permiten archivos JPG, PNG, GIF y WebP')
            
            # Validar que sea una imagen valida
            try:
                img = PIL.Image.open(photo)
                img.verify()
                
                # Validar formato de imagen
                if img.format not in ALLOWED_IMAGE_TYPES:
                    raise ValidationError(f'Formato de imagen no permitido. Solo se permiten: {", ".join(ALLOWED_IMAGE_TYPES)}')
                
            except Exception:
                raise ValidationError('El archivo no es una imagen valida')
            
            # Validar dimensiones mínimas
            photo.seek(0)  # Reset file pointer
            img = PIL.Image.open(photo)
            width, height = img.size

            if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                raise ValidationError(f'La imagen debe tener al menos {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION} píxeles')
            
            # Validar relación de aspecto extrema
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 10:
                raise ValidationError('La imagen tiene una relación de aspecto muy extrema')

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
            
            # Validar que no sean solo mayúsculas (excepto si es muy corto)
            if len(description) > 20 and description.isupper():
                raise ValidationError('Evita escribir todo en mayúsculas')
            
            # Validar palabras prohibidas o spam
            spam_words = ['test', 'testing', 'prueba', 'asdfgh', 'qwerty']
            if any(word in description.lower() for word in spam_words):
                raise ValidationError('Por favor, proporciona una descripción real del incidente')
        
        return description

    def clean_latitude(self):
        """Validación específica para latitud"""
        latitude = self.cleaned_data.get('latitude')
        
        if latitude is not None:
            try:
                lat_float = float(latitude)
                # Validar rango de latitud válido
                if not -90 <= lat_float <= 90:
                    raise ValidationError('La latitud debe estar entre -90 y 90 grados')
            except (ValueError, TypeError):
                raise ValidationError('La latitud debe ser un número válido')
        
        return latitude

    def clean_longitude(self):
        """Validación específica para longitud"""
        longitude = self.cleaned_data.get('longitude')
        
        if longitude is not None:
            try:
                lng_float = float(longitude)
                # Validar rango de longitud válido
                if not -180 <= lng_float <= 180:
                    raise ValidationError('La longitud debe estar entre -180 y 180 grados')
            except (ValueError, TypeError):
                raise ValidationError('La longitud debe ser un número válido')
        
        return longitude

    def clean(self):
        """Validaciones que involucran múltiples campos"""
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')
        
        # Validar que se hayan proporcionado coordenadas
        if not lat or not lng:
            raise ValidationError('Debe seleccionar una ubicacion en el mapa')
        
        # Validar que las coordenadas estén dentro de un rango razonable para Lima, Perú
        # (opcional - puedes ajustar estos valores según tu área de cobertura)
        if lat and lng:
            try:
                lat_float = float(lat)
                lng_float = float(lng)
                
                # Coordenadas aproximadas para Arequipa y alrededores
                # Latitud: -16.6 a -16.2, Longitud: -71.7 a -71.3
                if not (-16.6 <= lat_float <= -16.2) or not (-71.7 <= lng_float <= -71.3):
                    # Solo advertencia, no error crítico
                    self.add_error('latitude', 'La ubicacion parece estar fuera del area de Arequipa')
                    
            except (ValueError, TypeError):
                pass  # Ya se valida en clean_latitude y clean_longitude
        
        return cleaned_data

    def save(self, commit=True):
        """Personalizar el guardado del formulario"""
        instance = super().save(commit=False)
        
        # Limpiar y formatear datos antes de guardar
        if instance.title:
            instance.title = instance.title.strip()
        
        if instance.description:
            instance.description = instance.description.strip()
        
        if commit:
            instance.save()
        
        return instance