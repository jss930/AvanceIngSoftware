from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class ReporteColaborativo(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    usuario_reportador = models.ForeignKey(User, on_delete=models.CASCADE)
    ubicacion = models.CharField(max_length=100)
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
    

class InteraccionUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    reporte = models.ForeignKey('Reporte', on_delete=models.CASCADE)  # Asumiendo que tienes un modelo Reporte
    fecha_vista = models.DateTimeField(auto_now=True)
    tiempo_lectura_segundos = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'interaccion_usuario'
        unique_together = ['usuario', 'reporte']


class ConfiguracionUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    reportes_por_pagina = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(5), MaxValueValidator(50)]
    )
    mostrar_estadisticas = models.BooleanField(default=True)
    notificaciones_activas = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'configuracion_usuario'


class Reporte(models.Model):
    TIPOS_INCIDENTE = [
        ('accidente', 'Accidente'),
        ('congestion', 'Congestión'),
        ('obra', 'Obra en construcción'),
        ('manifestacion', 'Manifestación'),
        ('vehiculo_varado', 'Vehículo varado'),
        ('otro', 'Otro')
    ]
    
    ESTADOS_REPORTE = [
        ('pendiente', 'Pendiente'),
        ('validado', 'Validado'),
        ('rechazado', 'Rechazado'),
        ('archivado', 'Archivado')
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    usuario_reportador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reportes')
    latitud = models.DecimalField(max_digits=10, decimal_places=8)
    longitud = models.DecimalField(max_digits=11, decimal_places=8)
    tipo_incidente = models.CharField(max_length=20, choices=TIPOS_INCIDENTE)
    estado_reporte = models.CharField(max_length=20, choices=ESTADOS_REPORTE, default='pendiente')
    nivel_peligro = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(3)])
    imagen_geolocalizada = models.ImageField(upload_to='reportes/', null=True, blank=True)
    votos_positivos = models.IntegerField(default=0)
    votos_negativos = models.IntegerField(default=0)
    es_validado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario_reportador.username}"
    
    @property
    def ubicacion(self):
        return f"Lat: {self.latitud}, Lng: {self.longitud}"

    class Meta:
        db_table = 'reporte_trafico'
        indexes = [
            models.Index(fields=['usuario_reportador']),
            models.Index(fields=['estado_reporte']),
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['tipo_incidente']),
        ]