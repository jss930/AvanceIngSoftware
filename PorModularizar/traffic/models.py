from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import os

def validate_image_size(image):
    """Validar que la imagen no sea muy grande (máximo 5MB)"""
    if image.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError('La imagen no puede ser mayor a 5MB')

def validate_image_extension(image):
    """Validar extensión de imagen personalizada"""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f'Formato no válido. Use: {", ".join(valid_extensions)}')

class TrafficIncident(models.Model):
    INCIDENT_TYPES = [
        ('accident', 'Accidente'),
        ('construction', 'Construcción'),
        ('congestion', 'Congestión'),
        ('road_closure', 'Cierre de vía'),
        ('weather', 'Condiciones climáticas'),
        ('other', 'Otro'),
    ]
    
    # Campos requeridos
    title = models.CharField(max_length=100, help_text="Título del incidente")
    description = models.TextField(help_text="Descripción detallada del incidente")
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES, 
                                   help_text="Tipo de incidente")
    
    # Campos opcionales
    photo = models.ImageField(
        upload_to='incident_photos/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size,
        ],
        help_text="Foto del incidente (opcional, máximo 5MB)"
    )
    
    # Ubicación
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def clean(self):
        """Validaciones personalizadas a nivel de modelo"""
        super().clean()
        
        # Validar que la descripción tenga al menos 10 caracteres
        if len(self.description.strip()) < 10:
            raise ValidationError({
                'description': 'La descripción debe tener al menos 10 caracteres'
            })
        
        # Validar coordenadas (ejemplo para Perú)
        if not (-18.5 <= float(self.latitude) <= -0.5):
            raise ValidationError({
                'latitude': 'Latitud fuera del rango válido para Perú'
            })
        
        if not (-81.5 <= float(self.longitude) <= -68.5):
            raise ValidationError({
                'longitude': 'Longitud fuera del rango válido para Perú'
            })