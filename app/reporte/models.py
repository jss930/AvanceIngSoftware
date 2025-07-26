"""
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ReporteColaborativo(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario_reportador = models.ForeignKey(User, on_delete=models.CASCADE)
    ubicacion = models.CharField(max_length=100, blank=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    tipo_incidente = models.CharField(max_length=50)
    imagen_geolocalizada = models.ImageField(upload_to='reportes/', null=True, blank=True)
    estado_reporte = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('probado', 'Probado'),
            ('rechazado', 'Rechazado')
        ],
        default='pendiente'
    )
    nivel_peligro = models.IntegerField(default=1)
    votos_positivos = models.IntegerField(default=0)
    votos_negativos = models.IntegerField(default=0)
    usuarios_votantes = models.ManyToManyField(User, related_name='votos_emitidos', blank=True)
    es_validado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.titulo} ({self.estado_reporte})"
    """



   # haber
   
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, FileExtensionValidator
from django.utils import timezone
from PIL import Image
import os
from decimal import Decimal
from .utils import reverse_geocode

class ReporteColaborativo(models.Model):
    """Modelo para reportes de incidentes de trafico"""
    
    # Tipos de incidentes disponibles
    INCIDENT_TYPES = [
        ('accidente', '🚗 Accidente'),
        ('construccion', '🚧 Construcción'),
        ('embotellamiento', '🚦 Embotellamiento'),
        ('cierre_via', '🚫 Cierre de vía'),
        ('control_policial', '👮 Control policial'),
        ('semaforo_danado', '🔴 Semáforo dañado'),
        ('bache', '🕳️ Bache'),
        ('inundacion', '💧 Inundación'),
        ('vehiculo_averiado', '🔧 Vehículo averiado'),
        ('manifestacion', '✊ Manifestación'),
        ('otro', '❓ Otro')
    ]
    
    # Campos principales
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título del incidente',
        help_text='Descripción breve del incidente (máximo 200 caracteres)',
        validators=[MinLengthValidator(5, 'El título debe tener al menos 5 caracteres')]
    )
    
    descripcion = models.TextField(
        max_length=1000,
        verbose_name='Descripción detallada',
        help_text='Describe el incidente con el mayor detalle posible',
        validators=[MinLengthValidator(10, 'La descripción debe tener al menos 10 caracteres')]
    )
    
    tipo_incidente = models.CharField(
        max_length=50,
        choices=INCIDENT_TYPES,
        verbose_name='Tipo de incidente',
        help_text='Selecciona el tipo de incidente que mejor describe la situación'
    )
    
    # Campos de ubicación
    latitud = models.DecimalField(
        default= Decimal('0.0'),
        max_digits=18,
        decimal_places=10,
        verbose_name='Latitud',
        help_text='Coordenada de latitud del incidente'
    )
    
    longitud = models.DecimalField(
        default= Decimal('0.0'),
        max_digits=18,
        decimal_places=10,
        verbose_name='Longitud',
        help_text='Coordenada de longitud del incidente'
    )
    
    # Campo para foto opcional
    foto = models.ImageField(
        upload_to='reportes/%Y/%m/%d/',
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
    usuario_reportador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario reportante',
        help_text='Usuario que reportó el incidente'
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
        help_text='Fecha y hora cuando se creó el reporte'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización',
        help_text='Fecha y hora de la última actualización'
    )
    
    # Campos adicionales para funcionalidad avanzada
    estado_reporte = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('probado', 'Probado'),
            ('rechazado', 'Rechazado')
        ],
        default='pendiente'
    )
    
    """""
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
    ) """
    nivel_peligro = models.IntegerField(
        choices=[
            (1, '🟢 Bajo'), 
            (2, '🟡 Medio'), 
            (3, '🔴 Alto'), 
            (4, '🚨 Crítico')
        ],
        default=1
    )

    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Número de vistas',
        help_text='Cuántas veces se ha visto este incidente'
    )
    
    # Campos para geolocalización adicional
    nombre_via = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Nombre de la vía',
        help_text='Nombre de la vía donde ocurrió el incidente'
    )
    
    distrito = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Distrito',
        help_text='Distrito donde ocurrió el incidente'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="¿Está activo?",
        help_text="Marca si el reporte sigue siendo válido o visible"
    )
    votos_positivos = models.IntegerField(default=0)
    votos_negativos = models.IntegerField(default=0)
    usuarios_votantes = models.ManyToManyField(User, related_name='votos_emitidos', blank=True)
    
    class Meta:
        verbose_name = 'Incidente de Tráfico'
        verbose_name_plural = 'Incidentes de Tráfico'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['tipo_incidente']),
            models.Index(fields=['usuario_reportador']),
            models.Index(fields=['latitud', 'longitud']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.titulo} ({self.estado_reporte})"


    def save(self, *args, **kwargs):
        #Personaliza el guardado del modelo
        # 1. Limpiar campos de texto
        if self.titulo:
            self.titulo = self.titulo.strip()
        if self.descripcion:
            self.descripcion = self.descripcion.strip()

        # 2. Autocompletar dirección si latitud y longitud están presentes
        if self.latitud and self.longitud and (not self.nombre_via or not self.distrito):
            from .utils import reverse_geocode
            info = reverse_geocode(self.latitud, self.longitud)

            if "error" not in info:
                self.nombre_via = info.get("calle", "Desconocido")
                self.distrito = info.get("distrito", "Desconocido")
            else:
                print(f"⚠️ No se pudo obtener dirección: {info['error']}")

        # 3. Guardar primero el objeto (incluye imagen en disco)
        super().save(*args, **kwargs)

        # 4. Validar y procesar imagen si existe
        if self.foto:
            try:
                self.validate_and_process_image()
            except Exception as e:
                print(f"⚠️ Error procesando la imagen: {e}")

        
    def validate_and_process_image(self):
        """Validar y procesar la imagen subida"""
        if self.foto:
            # Validar tamaño del archivo (5MB máximo)
            if self.foto.size > 5 * 1024 * 1024:
                raise ValueError('La imagen no puede ser mayor a 5MB')
            
            # Abrir y validar la imagen
            try:
                img = Image.open(self.foto)
                img.verify()
                
                # Reabrir para procesar (verify() cierra el archivo)
                img = Image.open(self.foto)

                # Redimensionar si es muy grande
                max_dimension = 1920
                if img.width > max_dimension or img.height > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                    
                    # Guardar imagen redimensionada si el archivo existe
                    if os.path.exists(self.foto.path):
                        img.save(self.foto.path, optimize=True, quality=85)

            except Exception as e:
                raise ValueError(f'Error procesando la imagen: {str(e)}')
    
    def get_coordinates(self):
        """Retorna las coordenadas como tupla"""
        return (float(self.latitud), float(self.longitud))

    def get_google_maps_url(self):
        """Genera URL de Google Maps para la ubicación"""
        return f"https://www.google.com/maps?q={self.latitud},{self.longitud}"

    def get_distance_from(self, lat, lng):
        """Calcula la distancia desde una coordenada dada (en km)"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convertir grados a radianes
        lat1, lng1 = radians(float(self.latitud)), radians(float(self.longitud))
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
        return self.fecha_creacion >= cutoff_time
    
    def get_age_display(self):
        """Retorna una descripción amigable de la antigüedad del reporte"""
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - self.fecha_creacion

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
            1: '#28a745',      # Verde
            2: '#ffc107',   # Amarillo
            3: '#fd7e14',     # Naranja
            4: '#dc3545'  # Rojo
        }
        return colors.get(self.nivel_peligro, '#6c757d')
    
    def can_be_edited_by(self, user):
        """Verifica si un usuario puede editar este incidente"""
        if not user.is_authenticated:
            return False
        
        # El usuario que lo creó puede editarlo dentro de las primeras 2 horas
        if self.usuario_reportador == user:
            from datetime import timedelta
            cutoff_time = timezone.now() - timedelta(hours=2)
            return self.fecha_creacion >= cutoff_time
        
        # Los superusers siempre pueden editar
        return user.is_superuser
    
    @classmethod
    def get_recent_incidents(cls, hours=24, limit=50):
        """Obtiene incidentes recientes"""
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(
            fecha_creacion__gte=cutoff_time,
            is_active=True
        ).select_related('usuario_reportador').order_by('-fecha_creacion')[:limit]

    @classmethod
    def get_incidents_by_type(cls, tipo_incidente, limit=50):
        """Obtiene incidentes por tipo"""
        return cls.objects.filter(
            tipo_incidente=tipo_incidente,
            is_active=True
        ).select_related('usuario_reportador').order_by('-fecha_creacion')[:limit]

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


class Alerta(models.Model):
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    enviado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_enviadas')
    destinatarios = models.ManyToManyField(User, related_name='alertas_recibidas')
    ubicacion = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return f"{self.titulo} - {self.fecha_envio.strftime('%Y-%m-%d %H:%M')}"
