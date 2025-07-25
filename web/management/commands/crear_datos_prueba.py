# web/management/commands/crear_datos_prueba.py
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from web.models import Reporte, Ubicacion  # Asumiendo que Ubicacion está en models
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    """
    Comando para crear datos de prueba de reportes de tráfico
    
    Ejemplos de uso:
    python manage.py crear_datos_prueba --usuario=admin --cantidad=50
    python manage.py crear_datos_prueba --usuario=testuser --cantidad=100 --dias=60
    python manage.py crear_datos_prueba --usuario=admin --solo-validados
    """
    
    help = 'Crea datos de prueba para reportes de tráfico en Arequipa'
    
    # Configuración de datos de prueba (estilo cookbook)
    TIPOS_INCIDENTE = [
        'accidente', 'congestion', 'obra', 'manifestacion', 
        'vehiculo_varado', 'semaforo_dañado', 'evento_especial', 'otro'
    ]
    
    ESTADOS_REPORTE = ['pendiente', 'validado', 'rechazado', 'archivado']
    
    # Coordenadas base de Arequipa
    AREQUIPA_LAT_BASE = -16.4040
    AREQUIPA_LNG_BASE = -71.5340
    RADIO_VARIACION = 0.08  # Radio de variación en grados
    
    # Frases para nivel de peligro automático
    FRASES_PELIGRO_ALTO = ['muerte', 'choque', 'fatal', 'grave', 'ambulancia', 'bomberos']
    FRASES_PELIGRO_MEDIO = ['herido', 'congestion', 'colision', 'lesionado', 'tráfico denso']
    
    # URLs de imágenes de ejemplo para geolocalización
    IMAGENES_EJEMPLO = [
        'https://ejemplo.com/imagen1.jpg',
        'https://ejemplo.com/imagen2.jpg', 
        'https://ejemplo.com/imagen3.jpg',
        None  # Algunos reportes sin imagen
    ]
    
    # Plantillas de descripciones por tipo
    DESCRIPCIONES_PLANTILLA = {
        'accidente': [
            "Accidente vehicular reportado en la vía. Tráfico afectado.",
            "Colisión múltiple causa congestión en la zona.",
            "Vehículo accidentado obstruye parcialmente la vía."
        ],
        'congestion': [
            "Alta congestión vehicular en hora pico.",
            "Tráfico denso reportado por múltiples usuarios.",
            "Flujo vehicular lento debido a alta demanda."
        ],
        'obra': [
            "Obras de mantenimiento vial en progreso.",
            "Construcción de infraestructura afecta el tráfico.",
            "Reparación de pavimento causa desvíos."
        ],
        'manifestacion': [
            "Manifestación pacífica afecta el tráfico.",
            "Evento público causa cierre temporal de vías.",
            "Concentración ciudadana en la zona."
        ],
        'vehiculo_varado': [
            "Vehículo varado obstruye carril de circulación.",
            "Avería mecánica causa reducción de carriles.",
            "Vehículo de carga averiado en la vía principal.",
            "Auto detenido por falla mecánica en zona crítica."
        ],
        'semaforo_dañado': [
            "Semáforo fuera de servicio causa confusión en intersección.",
            "Falla en sistema de semaforización genera caos vehicular.",
            "Semáforo con intermitencias afecta fluidez del tráfico.",
            "Sistema de semáforos colapsado por corte eléctrico."
        ],
        'evento_especial': [
            "Evento deportivo genera alta concentración vehicular.",
            "Celebración religiosa afecta rutas principales.",
            "Concierto masivo causa desvíos de tráfico.",
            "Feria local modifica patrones de circulación."
        ],
        'otro': [
            "Incidente no categorizado reportado en la zona.",
            "Situación especial afecta el tráfico normal.",
            "Evento imprevisto causa alteración vial."
        ]
    }

    def add_arguments(self, parser):
        """Define argumentos del comando (estilo cookbook)"""
        parser.add_argument(
            '--usuario',
            type=str,
            required=True,
            help='Username del usuario para crear reportes'
        )
        
        parser.add_argument(
            '--cantidad',
            type=int,
            default=10,
            help='Cantidad de reportes a crear (default: 10)'
        )
        
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Rango de días hacia atrás para fechas aleatorias (default: 30)'
        )
        
        parser.add_argument(
            '--solo-validados',
            action='store_true',
            help='Crear solo reportes con estado "validado"'
        )
        
        parser.add_argument(
            '--zona',
            choices=['centro', 'norte', 'sur', 'este', 'oeste', 'todas'],
            default='todas',
            help='Zona específica de Arequipa para generar reportes'
        )

    def handle(self, *args, **options):
        """Método principal del comando (estilo cookbook)"""
        try:
            # Validar y obtener usuario
            usuario = self._obtener_usuario(options['usuario'])
            
            # Configurar parámetros
            cantidad = options['cantidad']
            dias_rango = options['dias']
            solo_validados = options['solo_validados']
            zona = options['zona']
            
            # Mostrar información inicial
            self._mostrar_info_inicial(usuario.username, cantidad, dias_rango, zona)
            
            # Crear reportes
            reportes_creados = self._crear_reportes(
                usuario, cantidad, dias_rango, solo_validados, zona
            )
            
            # Mostrar resumen final
            self._mostrar_resumen_final(reportes_creados, usuario.username)
            
        except CommandError:
            # Los CommandError ya muestran el mensaje, solo necesitamos salir
            return
        except Exception as e:
            raise CommandError(f'Error inesperado: {str(e)}')

    def _obtener_usuario(self, username):
        """Obtiene y valida el usuario (método auxiliar cookbook)"""
        if not username:
            raise CommandError('Debes especificar un usuario con --usuario')
        
        try:
            usuario = User.objects.get(username=username)
            self.stdout.write(f'✓ Usuario encontrado: {usuario.username}')
            return usuario
        except User.DoesNotExist:
            raise CommandError(f'Usuario "{username}" no encontrado')

    def _obtener_coordenadas_zona(self, zona):
        """Obtiene coordenadas base según la zona (método auxiliar cookbook)"""
        coordenadas_zona = {
            'centro': (-16.3990, -71.5350),
            'norte': (-16.3800, -71.5300),
            'sur': (-16.4200, -71.5400),
            'este': (-16.4000, -71.5100),
            'oeste': (-16.4000, -71.5600),
            'todas': (self.AREQUIPA_LAT_BASE, self.AREQUIPA_LNG_BASE)
        }
        return coordenadas_zona.get(zona, (self.AREQUIPA_LAT_BASE, self.AREQUIPA_LNG_BASE))

    def _generar_coordenadas_aleatorias(self, zona):
        """Genera coordenadas aleatorias según la zona (método auxiliar cookbook)"""
        lat_base, lng_base = self._obtener_coordenadas_zona(zona)
        
        latitud = lat_base + random.uniform(-self.RADIO_VARIACION, self.RADIO_VARIACION)
        longitud = lng_base + random.uniform(-self.RADIO_VARIACION, self.RADIO_VARIACION)
        
        return latitud, longitud

    def _generar_descripcion_con_peligro(self, tipo_incidente):
        """Genera descripción que puede afectar el nivel de peligro automático"""
        plantillas = self.DESCRIPCIONES_PLANTILLA.get(tipo_incidente, self.DESCRIPCIONES_PLANTILLA['otro'])
        descripcion_base = random.choice(plantillas)
        
        # Posibilidad de agregar frases que cambien el nivel de peligro
        if random.random() > 0.8:  # 20% probabilidad de peligro alto
            frase_peligro = random.choice(self.FRASES_PELIGRO_ALTO)
            descripcion_base += f" Reportes indican {frase_peligro} en el lugar."
        elif random.random() > 0.6:  # 40% probabilidad de peligro medio  
            frase_peligro = random.choice(self.FRASES_PELIGRO_MEDIO)
            descripcion_base += f" Se reporta {frase_peligro} en la zona."
        
        # Agregar detalles adicionales aleatorios
        detalles_extra = [
            f" Tiempo estimado de afectación: {random.randint(15, 120)} minutos.",
            " Se recomienda usar rutas alternas.",
            " Autoridades notificadas del incidente.",
            f" Nivel de impacto vehicular: {'alto' if random.random() > 0.7 else 'moderado'}."
        ]
        
        if random.random() > 0.5:
            descripcion_base += random.choice(detalles_extra)
        
        return descripcion_base

    def _calcular_nivel_peligro_automatico(self, descripcion):
        """Calcula el nivel de peligro basado en la descripción (como en ReporteColaborativo)"""
        desc_lower = descripcion.lower()
        
        # Revisar frases de peligro alto
        for frase in self.FRASES_PELIGRO_ALTO:
            if frase in desc_lower:
                return 3
        
        # Revisar frases de peligro medio
        for frase in self.FRASES_PELIGRO_MEDIO:
            if frase in desc_lower:
                return 2
        
        # Peligro bajo por defecto
        return 1

    def _crear_ubicacion(self, latitud, longitud):
        """Crea objeto Ubicacion (adaptar según tu implementación)"""
        # Asumiendo que tienes un modelo Ubicacion, si no, ajusta según tu implementación
        try:
            ubicacion, created = Ubicacion.objects.get_or_create(
                latitud=latitud,
                longitud=longitud,
                defaults={
                    'direccion_aproximada': f'Coordenadas: {latitud:.4f}, {longitud:.4f}',
                    'distrito': 'Arequipa',  # Ajustar según tu lógica
                }
            )
            return ubicacion
        except Exception:
            # Si no tienes modelo Ubicacion, return None y maneja en el modelo Reporte
            return None

    def _crear_reportes(self, usuario, cantidad, dias_rango, solo_validados, zona):
        """Crea los reportes de prueba (método principal cookbook)"""
        reportes_creados = 0
        ahora = timezone.now()
        
        self.stdout.write('Creando reportes...')
        
        for i in range(cantidad):
            try:
                # Seleccionar tipo y estado
                tipo_incidente = random.choice(self.TIPOS_INCIDENTE)
                
                if solo_validados:
                    estado_reporte = 'validado'
                else:
                    estado_reporte = random.choice(self.ESTADOS_REPORTE)
                
                # Generar fecha aleatoria
                dias_atras = random.randint(0, dias_rango)
                fecha_creacion = ahora - timedelta(days=dias_atras)
                
                # Generar coordenadas según zona
                latitud, longitud = self._generar_coordenadas_aleatorias(zona)
                
                # Crear ubicación (si tienes modelo Ubicacion)
                ubicacion = self._crear_ubicacion(latitud, longitud)
                
                # Generar descripción que puede afectar nivel de peligro
                descripcion = self._generar_descripcion_con_peligro(tipo_incidente)
                
                # Calcular nivel de peligro automático basado en descripción
                nivel_peligro = self._calcular_nivel_peligro_automatico(descripcion)
                
                # Generar imagen geolocalizaada (ocasionalmente)
                imagen_geolocalizada = random.choice(self.IMAGENES_EJEMPLO) if random.random() > 0.7 else None
                
                # Simular votaciones realistas según estado
                if estado_reporte == 'validado':
                    votos_positivos = random.randint(5, 25)
                    votos_negativos = random.randint(0, 3)
                elif estado_reporte == 'rechazado':
                    votos_positivos = random.randint(0, 5)
                    votos_negativos = random.randint(3, 15)
                else:
                    votos_positivos = random.randint(0, 10)
                    votos_negativos = random.randint(0, 5)
                
                # Crear reporte adaptado a tu ReporteColaborativo
                reporte = Reporte.objects.create(
                    titulo=f"Reporte de {tipo_incidente.replace('_', ' ').title()} #{i+1:03d}",
                    descripcion=descripcion,
                    usuario_reportador=usuario,
                    latitud=latitud,
                    longitud=longitud,
                    # ubicacion=ubicacion,  # Descomenta si tienes campo ubicacion
                    tipo_incidente=tipo_incidente,
                    estado_reporte=estado_reporte,
                    nivel_peligro=nivel_peligro,  # Calculado automáticamente
                    imagen_geolocalizada=imagen_geolocalizada,
                    votos_positivos=votos_positivos,
                    votos_negativos=votos_negativos,
                    es_validado=(estado_reporte == 'validado'),
                    fecha_creacion=fecha_creacion,
                    fecha_actualizacion=fecha_creacion
                )
                
                reportes_creados += 1
                
                # Mostrar progreso cada 10 elementos
                if (i + 1) % 10 == 0:
                    self.stdout.write(f'  → Creados {i + 1}/{cantidad} reportes...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Error creando reporte #{i+1}: {str(e)}')
                )
                continue
        
        return reportes_creados

    def _mostrar_info_inicial(self, username, cantidad, dias_rango, zona):
        """Muestra información inicial del comando (método auxiliar cookbook)"""
        self.stdout.write(
            self.style.HTTP_INFO('=' * 60)
        )
        self.stdout.write(
            self.style.HTTP_INFO('  CREADOR DE DATOS DE PRUEBA - REPORTES TRÁFICO')
        )
        self.stdout.write(
            self.style.HTTP_INFO('=' * 60)
        )
        self.stdout.write(f'Usuario: {username}')
        self.stdout.write(f'Cantidad a crear: {cantidad} reportes')
        self.stdout.write(f'Rango temporal: últimos {dias_rango} días')
        self.stdout.write(f'Zona: {zona}')
        self.stdout.write('')

    def _mostrar_resumen_final(self, reportes_creados, username):
        """Muestra resumen final de la ejecución (método auxiliar cookbook)"""
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ COMPLETADO: Se crearon {reportes_creados} reportes para {username}')
        )
        
        # Mostrar estadísticas adicionales
        total_reportes = Reporte.objects.filter(usuario_reportador__username=username).count()
        self.stdout.write(
            self.style.SUCCESS(f'✓ Total reportes del usuario: {total_reportes}')
        )
        
        self.stdout.write(
            self.style.SUCCESS('=' * 60)
        )
        
        # Sugerir comandos útiles
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('Comandos útiles para verificar:'))
        self.stdout.write(f'  python manage.py shell -c "from web.models import Reporte; print(Reporte.objects.filter(usuario_reportador__username=\'{username}\').count())"')
        self.stdout.write('  python manage.py limpiar_reportes_antiguos --dias=30')