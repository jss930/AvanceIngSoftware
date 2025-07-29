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



# ----
class HistorialNotificacion(models.Model):
    ESTADOS = [
        ('enviado', 'Enviado'),
        ('fallido', 'Fallido'), 
        ('pendiente', 'Pendiente'),
    ]
    
    TIPOS = [
        ('sistema', 'Sistema'),
        ('email', 'Email'),
        ('push', 'Push'),
        ('sms', 'SMS'),
    ]
    
    alerta = models.ForeignKey(Alerta, on_delete=models.CASCADE, related_name='historiales')
    usuario_destinatario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fecha_envio_real = models.DateTimeField(auto_now_add=True)
    estado_entrega = models.CharField(max_length=20, choices=ESTADOS, default='enviado')
    zona = models.CharField(max_length=255, blank=True)
    tipo_notificacion = models.CharField(max_length=50, choices=TIPOS, default='sistema')
    mensaje_error = models.TextField(blank=True, null=True)  # Para errores de entrega
    
    class Meta:
        verbose_name = "Historial de Notificación"
        verbose_name_plural = "Historiales de Notificaciones"
        ordering = ['-fecha_envio_real']
    
    def __str__(self):
        destinatario = self.usuario_destinatario.username if self.usuario_destinatario else "Todos"
        return f"{self.alerta.titulo} → {destinatario} ({self.fecha_envio_real.strftime('%d/%m/%Y %H:%M')})"