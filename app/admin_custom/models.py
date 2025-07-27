from django.db import models
from django.contrib.auth.models import User

# models.py
class Alerta(models.Model):
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)  # <-- AGREGADO
    enviado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_enviadas')
    destinatarios = models.ManyToManyField(User, related_name='alertas_recibidas')
    ubicacion = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return f"{self.titulo} - {self.fecha_envio.strftime('%Y-%m-%d %H:%M')}"
