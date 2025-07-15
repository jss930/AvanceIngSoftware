from django.db import models
from django.contrib.auth.models import User





# Create your models here.
class ReporteColaborativo(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario_reportador = models.ForeignKey(User, on_delete=models.CASCADE)
    ubicacion = models.CharField(max_length=100)
    tipo_incidente = models.CharField(max_length=50)
    estado_reporte = models.CharField(max_length=20, default='pendiente')  # probado, rechazado, pendiente

    def __str__(self):
        return f"{self.titulo} ({self.estado_reporte})"
    
    
    
    
   # haber
   
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, FileExtensionValidator
from django.utils import timezone
from PIL import Image
import os
from decimal import Decimal


class TrafficIncident(models.Model):
    """Modelo para reportes de incidentes de trafico"""
    
    # Tipos de incidentes disponibles
    INCIDENT_TYPES = [
        ('accident', '🚗 Accidente'),
        ('construction', '🚧 Construcción'),
        ('traffic_jam', '🚦 Embotellamiento'),
        ('road_closure', '🚫 Cierre de vía'),
        ('police_control', '👮 Control policial'),
        ('broken_traffic_light', '🔴 Semáforo dañado'),
        ('pothole', '🕳️ Bache'),
        ('flooding', '💧 Inundación'),
        ('vehicle_breakdown', '🔧 Vehículo averiado'),
        ('protest', '✊ Manifestación'),
        ('other', '❓ Otro')
    ]
    
    # Campos principales
    title = models.CharField(
        max_length=200,
        verbose_name='Título del incidente',
        help_text='Descripción breve del incidente (máximo 200 caracteres)',
        validators=[MinLengthValidator(5, 'El título debe tener al menos 5 caracteres')]
    )
    
    description = models.TextField(
        max_length=1000,
        verbose_name='Descripción detallada',
        help_text='Describe el incidente con el mayor detalle posible',
        validators=[MinLengthValidator(10, 'La descripción debe tener al menos 10 caracteres')]
    )
    
    incident_type = models.CharField(
        max_length=50,
        choices=INCIDENT_TYPES,
        verbose_name='Tipo de incidente',
        help_text='Selecciona el tipo de incidente que mejor describe la situación'
    )
    
    # Campos de ubicación
    latitude = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        verbose_name='Latitud',
        help_text='Coordenada de latitud del incidente'
    )
    
    longitude = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        verbose_name='Longitud',
        help_text='Coordenada de longitud del incidente'
    )
    
    # Campo para foto opcional
    photo = models.ImageField(
        upload_to='traffic_incidents/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Foto del incidente',
        help_text='Imagen opcional del incidente (máximo 5MB)',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'],
                message='Solo se permiten archivos JPG, PNG, GIF y WebP'
            )
        ]
    )
    
    # Relación con usuario
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario reportante',
        help_text='Usuario que reportó el incidente'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
        help_text='Fecha y hora cuando se creó el reporte'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización',
        help_text='Fecha y hora de la última actualización'
    )
    
    # Campos adicionales para funcionalidad avanzada
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el incidente sigue activo'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Verificado',
        help_text='Indica si el incidente ha sido verificado por moderadores'
    )
    
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', '🟢 Baja'),
            ('medium', '🟡 Media'),
            ('high', '🔴 Alta'),
            ('critical', '🚨 Crítica')
        ],
        default='medium',
        verbose_name='Severidad',
        help_text='Nivel de severidad del incidente'
    )
    
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Número de vistas',
        help_text='Cuántas veces se ha visto este incidente'
    )
    
    # Campos para geolocalización adicional
    address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Dirección',
        help_text='Dirección aproximada del incidente (se llena automáticamente)'
    )
    
    district = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Distrito',
        help_text='Distrito donde ocurrió el incidente'
    )
    
    class Meta:
        verbose_name = 'Incidente de Tráfico'
        verbose_name_plural = 'Incidentes de Tráfico'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['incident_type']),
            models.Index(fields=['user']),
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_incident_type_display()}: {self.title}"
    
    def save(self, *args, **kwargs):
        """Personalizar el guardado del modelo"""
        # Limpiar título y descripción
        if self.title:
            self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()
        
        # Guarda primero (Django guarda la imagen en disco)
        super().save(*args, **kwargs)
        
        
        # Validar y procesar imagen si existe
        if self.photo:
            try:
                self.validate_and_process_image()
            except Exception as e:
                print(f"⚠️ Error procesando la imagen: {e}")
        
        
    
    def validate_and_process_image(self):
        """Validar y procesar la imagen subida"""
        if self.photo:
            # Validar tamaño del archivo (5MB máximo)
            if self.photo.size > 5 * 1024 * 1024:
                raise ValueError('La imagen no puede ser mayor a 5MB')
            
            # Abrir y validar la imagen
            try:
                img = Image.open(self.photo)
                img.verify()
                
                # Reabrir para procesar (verify() cierra el archivo)
                img = Image.open(self.photo)
                
                # Redimensionar si es muy grande
                max_dimension = 1920
                if img.width > max_dimension or img.height > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                    
                    # Guardar imagen redimensionada si el archivo existe
                    if os.path.exists(self.photo.path):
                        img.save(self.photo.path, optimize=True, quality=85)
                
            except Exception as e:
                raise ValueError(f'Error procesando la imagen: {str(e)}')
    
    def get_coordinates(self):
        """Retorna las coordenadas como tupla"""
        return (float(self.latitude), float(self.longitude))
    
    def get_google_maps_url(self):
        """Genera URL de Google Maps para la ubicación"""
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
    
    def get_distance_from(self, lat, lng):
        """Calcula la distancia desde una coordenada dada (en km)"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convertir grados a radianes
        lat1, lng1 = radians(float(self.latitude)), radians(float(self.longitude))
        lat2, lng2 = radians(lat), radians(lng)
        
        # Fórmula de Haversine
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radio de la Tierra en km
        r = 6371
        
        return round(c * r, 2)
    
    def is_recent(self, hours=24):
        """Verifica si el incidente es reciente (últimas X horas)"""
        from datetime import timedelta
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return self.created_at >= cutoff_time
    
    def get_age_display(self):
        """Retorna una descripción amigable de la antigüedad del reporte"""
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"hace {hours} hora{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "hace unos segundos"
    
    def increment_views(self):
        """Incrementa el contador de vistas"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def get_severity_color(self):
        """Retorna el color CSS para la severidad"""
        colors = {
            'low': '#28a745',      # Verde
            'medium': '#ffc107',   # Amarillo
            'high': '#fd7e14',     # Naranja
            'critical': '#dc3545'  # Rojo
        }
        return colors.get(self.severity, '#6c757d')
    
    def can_be_edited_by(self, user):
        """Verifica si un usuario puede editar este incidente"""
        if not user.is_authenticated:
            return False
        
        # El usuario que lo creó puede editarlo dentro de las primeras 2 horas
        if self.user == user:
            from datetime import timedelta
            cutoff_time = timezone.now() - timedelta(hours=2)
            return self.created_at >= cutoff_time
        
        # Los superusers siempre pueden editar
        return user.is_superuser
    
    @classmethod
    def get_recent_incidents(cls, hours=24, limit=50):
        """Obtiene incidentes recientes"""
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(
            created_at__gte=cutoff_time,
            is_active=True
        ).select_related('user').order_by('-created_at')[:limit]
    
    @classmethod
    def get_incidents_by_type(cls, incident_type, limit=50):
        """Obtiene incidentes por tipo"""
        return cls.objects.filter(
            incident_type=incident_type,
            is_active=True
        ).select_related('user').order_by('-created_at')[:limit]
    
    @classmethod
    def get_incidents_near(cls, latitude, longitude, radius_km=5):
        """Obtiene incidentes cerca de una ubicación (requiere PostGIS para ser más eficiente)"""
        # Implementación básica sin PostGIS
        # Para producción, considera usar PostGIS con ST_DWithin
        incidents = cls.objects.filter(is_active=True)
        nearby_incidents = []
        
        for incident in incidents:
            distance = incident.get_distance_from(latitude, longitude)
            if distance <= radius_km:
                nearby_incidents.append((incident, distance))
        
        # Ordenar por distancia
        nearby_incidents.sort(key=lambda x: x[1])
        return [incident for incident, distance in nearby_incidents]


# Modelo para comentarios en incidentes (opcional)
class IncidentComment(models.Model):
    """Modelo para comentarios en incidentes"""
    
    incident = models.ForeignKey(
        TrafficIncident,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Incidente'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    
    comment = models.TextField(
        max_length=500,
        verbose_name='Comentario',
        validators=[MinLengthValidator(5, 'El comentario debe tener al menos 5 caracteres')]
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        verbose_name = 'Comentario de Incidente'
        verbose_name_plural = 'Comentarios de Incidentes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comentario de {self.user.username} en {self.incident.title}"


# Modelo para votos/reacciones en incidentes (opcional)
class IncidentVote(models.Model):
    """Modelo para votos/confirmaciones de incidentes"""
    
    VOTE_TYPES = [
        ('confirm', '✅ Confirmar'),
        ('deny', '❌ Desmentir'),
        ('resolved', '✔️ Resuelto')
    ]
    
    incident = models.ForeignKey(
        TrafficIncident,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='Incidente'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    
    vote_type = models.CharField(
        max_length=20,
        choices=VOTE_TYPES,
        verbose_name='Tipo de voto'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de voto'
    )
    
    class Meta:
        verbose_name = 'Voto de Incidente'
        verbose_name_plural = 'Votos de Incidentes'
        unique_together = ['incident', 'user']  # Un usuario solo puede votar una vez por incidente
    
    def __str__(self):
        return f"{self.user.username} - {self.get_vote_type_display()}" 