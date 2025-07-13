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