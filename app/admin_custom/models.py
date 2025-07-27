from django.db import models
from django.contrib.auth.models import User

class Alerta(models.Model):
    PRIORIDADES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    destinatarios = models.ManyToManyField(User, blank=True)
    ubicacion = models.CharField(max_length=255, blank=True, null=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    fecha_envio = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    enviado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_enviadas')
    enviar_a_todos = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
