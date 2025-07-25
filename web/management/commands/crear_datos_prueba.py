from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from web.models import Reporte
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Crea datos de prueba para reportes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Username del usuario para crear reportes'
        )
        parser.add_argument(
            '--cantidad',
            type=int,
            default=10,
            help='Cantidad de reportes a crear'
        )
    
    def handle(self, *args, **options):
        username = options.get('usuario')
        cantidad = options['cantidad']
        
        if not username:
            self.stdout.write(
                self.style.ERROR('Debes especificar un usuario con --usuario')
            )
            return
        
        try:
            usuario = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuario {username} no encontrado')
            )
            return
        
        tipos_incidente = ['accidente', 'congestion', 'obra', 'manifestacion', 'vehiculo_varado', 'otro']
        estados = ['pendiente', 'validado', 'rechazado', 'archivado']
        
        reportes_creados = 0
        
        for i in range(cantidad):
            tipo = random.choice(tipos_incidente)
            estado = random.choice(estados)
            
            # Crear fechas aleatorias en los últimos 30 días
            dias_atras = random.randint(0, 30)
            fecha_creacion = datetime.now() - timedelta(days=dias_atras)
            
            reporte = Reporte.objects.create(
                titulo=f"Reporte de {tipo.title()} #{i+1}",
                descripcion=f"Descripción del {tipo} reportado en la zona. "
                           f"Incidente de nivel {'alto' if random.random() > 0.7 else 'medio'}.",
                usuario_reportador=usuario,
                latitud=-16.4040 + random.uniform(-0.05, 0.05),  # Arequipa aprox
                longitud=-71.5340 + random.uniform(-0.05, 0.05),
                tipo_incidente=tipo,
                estado_reporte=estado,
                nivel_peligro=random.randint(1, 3),
                votos_positivos=random.randint(0, 20),
                votos_negativos=random.randint(0, 5),
                es_validado=(estado == 'validado')
            )
            
            # Actualizar fecha de creación
            reporte.fecha_creacion = fecha_creacion
            reporte.save()
            
            reportes_creados += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Se crearon {reportes_creados} reportes para el usuario {username}'
            )
        )