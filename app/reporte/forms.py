"""
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

    def clean_imagen_geolocalizada(self):
        imagen = self.cleaned_data.get('imagen_geolocalizada')
        if imagen:
            if imagen.size > MAX_PHOTO_SIZE:
                raise ValidationError(f'El tamaño máximo permitido es {MAX_PHOTO_SIZE / (1024 * 1024)} MB.')
            try:
                img = PIL.Image.open(imagen)
                if img.format not in ALLOWED_IMAGE_TYPES:
                    raise ValidationError(f'Formato de imagen no permitido. Debe ser uno de: {", ".join(ALLOWED_IMAGE_TYPES)}.')
                if img.width < MIN_IMAGE_DIMENSION or img.height < MIN_IMAGE_DIMENSION:
                    raise ValidationError(f'Las dimensiones mínimas de la imagen son {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION} píxeles.')
            except Exception as e:
                raise ValidationError(f'Error al procesar la imagen: {str(e)}')
        return imagen

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion and len(descripcion) < MIN_DESCRIPTION_LENGTH:
            raise ValidationError(f'La descripción debe tener al menos {MIN_DESCRIPTION_LENGTH} caracteres.')
        return descripcion
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import ReporteColaborativo
import PIL.Image
import os

MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5MB
MIN_DESCRIPTION_LENGTH = 10  # los caracteres mínimos para la descripción
MIN_IMAGE_DIMENSION = 100  # dimensiones mínimas de la imagen
ALLOWED_IMAGE_TYPES = ['JPEG', 'PNG', 'GIF', 'WEBP']

class ReporteColaborativoForm(forms.ModelForm):
    class Meta:
        model = ReporteColaborativo
        exclude = ['usuario_reportador', 'fecha_creacion', 'fecha_actualizacion',
                   'votos_positivos', 'votos_negativos', 'usuarios_votantes', 'es_validado',
                   'estado_reporte','views_count', 'is_active']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Accidente en Av. Principal',
                'maxlength': 200
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el incidente en detalle...',
                'maxlength': 1000
            }),
            'tipo_incidente': forms.Select(attrs={
                'class': 'form-control'
            }),
            'foto': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),

            'nivel_peligro': forms.Select(attrs={
                'class': 'form-control',
            })
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

    def clean_foto(self):
        """Validación específica para fotos"""
        foto = self.cleaned_data.get('foto')
        
        if foto:
            # Validar tamaño del archivo
            if foto.size > MAX_PHOTO_SIZE:
                raise ValidationError('La imagen no puede ser mayor a 5MB')
            
            # Validar extensión del archivo
            file_ext = os.path.splitext(foto.name)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                raise ValidationError('Solo se permiten archivos JPG, PNG, GIF y WebP')
            
            # Validar que sea una imagen valida
            try:
                img = PIL.Image.open(foto)
                img.verify()
                
                # Validar formato de imagen
                if img.format not in ALLOWED_IMAGE_TYPES:
                    raise ValidationError(f'Formato de imagen no permitido. Solo se permiten: {", ".join(ALLOWED_IMAGE_TYPES)}')
                
            except Exception:
                raise ValidationError('El archivo no es una imagen valida')
            
            # Validar dimensiones mínimas
            foto.seek(0)  # Reset file pointer
            img = PIL.Image.open(foto)
            width, height = img.size

            if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                raise ValidationError(f'La imagen debe tener al menos {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION} píxeles')
            
            # Validar relación de aspecto extrema
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 10:
                raise ValidationError('La imagen tiene una relación de aspecto muy extrema')

        return foto

    def clean_descripcion(self):
        """Validación específica para descripción"""
        descripcion = self.cleaned_data.get('descripcion')
        
        if descripcion:
            # Remover espacios extra
            descripcion = descripcion.strip()
            
            # Validar longitud mínima
            if len(descripcion) < MIN_DESCRIPTION_LENGTH:
                raise ValidationError(f'La descripción debe tener al menos {MIN_DESCRIPTION_LENGTH} caracteres')

            # Validar que no sea solo números o caracteres especiales
            if not any(c.isalpha() for c in descripcion):
                raise ValidationError('La descripción debe contener texto descriptivo')
            
            # Validar que no sean solo mayúsculas (excepto si es muy corto)
            if len(descripcion) > 20 and descripcion.isupper():
                raise ValidationError('Evita escribir todo en mayúsculas')
            
            # Validar palabras prohibidas o spam
            spam_words = ['test', 'testing', 'prueba', 'asdfgh', 'qwerty']
            if any(word in descripcion.lower() for word in spam_words):
                raise ValidationError('Por favor, proporciona una descripción real del incidente')

        return descripcion

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
        lat = cleaned_data.get('latitud')
        lng = cleaned_data.get('longitud')
        
        # Validar que se hayan proporcionado coordenadas
        if not lat or not lng:
            raise ValidationError('Debe seleccionar una ubicacion en el mapa')

        # Validar que las coordenadas estén dentro de un rango razonable para Arequipa, )
        if lat and lng:
            try:
                lat_float = float(lat)
                lng_float = float(lng)
                
                # Coordenadas aproximadas para Arequipa y alrededores
                # Latitud: -16.6 a -16.2, Longitud: -71.7 a -71.3
                if not (-16.6 <= lat_float <= -16.2) or not (-71.7 <= lng_float <= -71.3):
                    # Solo advertencia, no error crítico
                    self.add_error('latitud', 'La ubicacion parece estar fuera del area de Arequipa')
                    
            except (ValueError, TypeError):
                pass  # Ya se valida en clean_latitude y clean_longitude
        
        return cleaned_data

    def save(self, commit=True):
        """Personalizar el guardado del formulario"""
        instance = super().save(commit=False)
        
        # Limpiar y formatear datos antes de guardar
        if instance.titulo:
            instance.titulo = instance.titulo.strip()

        if instance.descripcion:
            instance.descripcion = instance.descripcion.strip()

        if commit:
            instance.save()
        
        return instance




