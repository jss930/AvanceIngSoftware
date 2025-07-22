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
    
class Alerta(models.Model):
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    enviado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_enviadas')
    destinatarios = models.ManyToManyField(User, related_name='alertas_recibidas')
    ubicacion = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return f"{self.titulo} - {self.fecha_envio.strftime('%Y-%m-%d %H:%M')}"
