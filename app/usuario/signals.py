# Crear archivo: app/usuario/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crear automáticamente un perfil cuando se crea un nuevo usuario
    """
    if created:
        PerfilUsuario.objects.create(
            usuario=instance,
            notificaciones_activas=True,
            radio_notificacion=2.0,
            frecuencia_actualizacion=30,
            tipos_incidentes_notificar=[
                'embotellamiento', 
                'accidente', 
                'construccion',
                'cierre_via'
            ]
        )

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Guardar el perfil cuando se guarda el usuario
    """
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
    else:
        # Si no existe perfil, crearlo
        PerfilUsuario.objects.get_or_create(
            usuario=instance,
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

# También agregar al archivo app/usuario/apps.py:

from django.apps import AppConfig

class UsuarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.usuario'

    def ready(self):
        import app.usuario.signals  # Importar los signals