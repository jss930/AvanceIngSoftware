from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal

class Alerta(models.Model):
    TIPOS_ALERTA = [
        ('emergencia', 'Emergencia'),
        ('trafico', 'Tráfico'),
        ('informativa', 'Informativa'),
        ('zona_peligrosa', 'Zona Peligrosa'),
    ]
    
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    tipo_alerta = models.CharField(max_length=20, choices=TIPOS_ALERTA)
    
    # Ubicación opcional
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    radio_cobertura = models.IntegerField(null=True, blank=True, help_text="Radio en metros")
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    es_activa = models.BooleanField(default=True)
    es_masiva = models.BooleanField(default=False)
    prioridad = models.IntegerField(default=1)
    
    # Relación con usuario creador
    usuario_creador_id = models.IntegerField()
    
    class Meta:
        db_table = 'alertas'
        ordering = ['-fecha_creacion', '-prioridad']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_tipo_alerta_display()}"

class ConfiguracionNotificacion(models.Model):
    usuario_id = models.IntegerField(unique=True)
    notificaciones_trafico_activas = models.BooleanField(default=True)
    radio_notificaciones = models.IntegerField(default=1000)  # metros
    tipos_incidentes_interes = models.JSONField(default=list)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'configuraciones_notificacion'
    
    def __str__(self):
        return f"Configuración Usuario {self.usuario_id}"
