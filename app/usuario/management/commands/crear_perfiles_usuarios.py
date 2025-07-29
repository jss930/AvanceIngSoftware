# Archivo: app/usuario/management/commands/crear_perfiles_usuarios.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.usuario.models import PerfilUsuario

class Command(BaseCommand):
    help = 'Crear perfiles para usuarios existentes que no tienen perfil'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Crear perfiles para todos los usuarios sin perfil',
        )

    def handle(self, *args, **options):
        usuarios_sin_perfil = User.objects.filter(perfil__isnull=True)
        
        if not usuarios_sin_perfil.exists():
            self.stdout.write(
                self.style.SUCCESS('Todos los usuarios ya tienen perfil')
            )
            return

        count = 0
        for usuario in usuarios_sin_perfil:
            PerfilUsuario.objects.create(
                usuario=usuario,
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
            count += 1
            self.stdout.write(f'Perfil creado para: {usuario.username}')

        self.stdout.write(
            self.style.SUCCESS(f'Se crearon {count} perfiles de usuario')
        )

# Para ejecutar el comando:
# python manage.py crear_perfiles_usuarios --all