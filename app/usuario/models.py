# app/usuario/models.py - ARCHIVO CORREGIDO

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class PerfilUsuario(models.Model):
    """Modelo para el perfil extendido del usuario"""
    
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    
    # Configuraciones de notificaciones
    notificaciones_activas = models.BooleanField(
        default=True,
        verbose_name='Notificaciones activas',
        help_text='Recibir notificaciones de zonas congestionadas'
    )
    
    radio_notificacion = models.FloatField(
        default=2.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(10.0)],
        verbose_name='Radio de notificación (km)',
        help_text='Distancia máxima para recibir notificaciones de congestión'
    )
    
    # Ubicación actual del usuario (se actualiza constantemente)
    latitud_actual = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        null=True,
        blank=True,
        verbose_name='Latitud actual'
    )
    
    longitud_actual = models.DecimalField(
        max_digits=18,
        decimal_places=10,
        null=True,
        blank=True,
        verbose_name='Longitud actual'
    )
    
    ultima_actualizacion_ubicacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última actualización de ubicación'
    )
    
    # Configuraciones adicionales
    frecuencia_actualizacion = models.IntegerField(
        default=30,
        validators=[MinValueValidator(10), MaxValueValidator(300)],
        verbose_name='Frecuencia de actualización (segundos)',
        help_text='Cada cuántos segundos actualizar la ubicación'
    )
    
    tipos_incidentes_notificar = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Tipos de incidentes a notificar',
        help_text='Lista de tipos de incidentes que quiere recibir'
    )
    
    # Campos adicionales para métricas
    total_notificaciones_recibidas = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de notificaciones recibidas'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación del perfil'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de última actualización'
    )
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        indexes = [
            models.Index(fields=['latitud_actual', 'longitud_actual'], name='perfil_ubicacion_idx'),
            models.Index(fields=['notificaciones_activas'], name='perfil_notif_idx'),
            models.Index(fields=['ultima_actualizacion_ubicacion'], name='perfil_ult_ubic_idx'),
        ]
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
    def get_tipos_incidentes_display(self):
        """Retorna los tipos de incidentes en formato legible"""
        if not self.tipos_incidentes_notificar:
            return "Todos"
        
        from app.reporte.models import ReporteColaborativo
        tipos_dict = dict(ReporteColaborativo.INCIDENT_TYPES)
        return ", ".join([tipos_dict.get(tipo, tipo) for tipo in self.tipos_incidentes_notificar])
    
    def get_ubicacion_actual(self):
        """Retorna la ubicación actual como tupla"""
        if self.latitud_actual and self.longitud_actual:
            return (float(self.latitud_actual), float(self.longitud_actual))
        return None
    
    def incrementar_notificaciones(self):
        """Incrementa el contador de notificaciones"""
        self.total_notificaciones_recibidas += 1
        self.save(update_fields=['total_notificaciones_recibidas'])
    
    def tiene_ubicacion_reciente(self, minutos=30):
        """Verifica si la ubicación es reciente"""
        if not self.ultima_actualizacion_ubicacion:
            return False
            
        from django.utils import timezone
        from datetime import timedelta
        
        limite = timezone.now() - timedelta(minutes=minutos)
        return self.ultima_actualizacion_ubicacion >= limite
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Obtiene o crea un perfil para el usuario"""
        perfil, created = cls.objects.get_or_create(
            usuario=user,
            defaults={
                'notificaciones_activas': True,
                'radio_notificacion': 2.0,
                'frecuencia_actualizacion': 30,
                'tipos_incidentes_notificar': [
                    'embotellamiento', 
                    'accidente', 
                    'construccion',
                    'cierre_via'
                ]
            }
        )
        return perfil
    
    @classmethod
    def get_usuarios_con_notificaciones_activas(cls):
        """Obtiene usuarios que tienen notificaciones activas"""
        return cls.objects.filter(
            notificaciones_activas=True,
            latitud_actual__isnull=False,
            longitud_actual__isnull=False
        ).select_related('usuario')
    
    def save(self, *args, **kwargs):
        """Personalización del guardado"""
        # Asegurar que hay tipos de incidentes por defecto
        if not self.tipos_incidentes_notificar:
            self.tipos_incidentes_notificar = [
                'embotellamiento', 
                'accidente', 
                'construccion',
                'cierre_via'
            ]
        
        super().save(*args, **kwargs)