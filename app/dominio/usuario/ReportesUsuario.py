# 1. ESTILO PERSISTENT-TABLES (Models)
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class PerfilUsuario(models.Model):
    """Tabla persistente para perfiles de usuario"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    puntos_acumulados = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_reportes = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    perfil_visible = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'perfil_usuario'
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['puntos_acumulados']),
        ]

class ContribucionUsuario(models.Model):
    """Tabla para tracking de contribuciones"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    reporte_id = models.IntegerField()
    puntos_otorgados = models.IntegerField(default=10)
    fecha_contribucion = models.DateTimeField(auto_now_add=True)
    tipo_contribucion = models.CharField(max_length=50, default='reporte')
    
    class Meta:
        db_table = 'contribucion_usuario'
        unique_together = ['usuario', 'reporte_id']


# 2. ESTILO ERROR/EXCEPTION HANDLING
class PerfilUsuarioError(Exception):
    """Excepción base para errores de perfil"""
    pass

class PerfilNoVisibleError(PerfilUsuarioError):
    """Excepción cuando el perfil no es visible"""
    pass

class UsuarioNoEncontradoError(PerfilUsuarioError):
    """Excepción cuando el usuario no existe"""
    pass

class PerfilNoExisteError(PerfilUsuarioError):
    """Excepción cuando el perfil no existe"""
    pass


# 3. ESTILO THINGS (Objetos con responsabilidades claras)
class PerfilUsuarioThing:
    """Objeto que encapsula la lógica de perfil de usuario"""
    
    def __init__(self, usuario_id: int):
        self.usuario_id = usuario_id
        self._perfil = None
        self._contribuciones = None
    
    @property
    def perfil(self):
        """Lazy loading del perfil"""
        if self._perfil is None:
            try:
                self._perfil = PerfilUsuario.objects.get(usuario_id=self.usuario_id)
            except PerfilUsuario.DoesNotExist:
                raise PerfilNoExisteError(f"Perfil no existe para usuario {self.usuario_id}")
        return self._perfil
    
    @property
    def contribuciones(self):
        """Lazy loading de contribuciones"""
        if self._contribuciones is None:
            self._contribuciones = ContribucionUsuario.objects.filter(
                usuario_id=self.usuario_id
            ).order_by('-fecha_contribucion')
        return self._contribuciones
    
    def es_visible(self) -> bool:
        """Verifica si el perfil es visible"""
        return self.perfil.perfil_visible
    
    def obtener_estadisticas(self) -> dict:
        """Obtiene estadísticas del perfil"""
        return {
            'puntos_totales': self.perfil.puntos_acumulados,
            'total_reportes': self.perfil.total_reportes,
            'promedio_puntos_por_reporte': self._calcular_promedio_puntos(),
            'contribuciones_recientes': self.contribuciones[:5]
        }
    
    def _calcular_promedio_puntos(self) -> float:
        """Calcula promedio de puntos por reporte"""
        if self.perfil.total_reportes == 0:
            return 0.0
        return self.perfil.puntos_acumulados / self.perfil.total_reportes
    
    def cambiar_visibilidad(self, visible: bool):
        """Cambia la visibilidad del perfil"""
        self.perfil.perfil_visible = visible
        self.perfil.save()


class ImagenMiniaturaCollector:
    """Colector de miniaturas de imágenes"""
    
    def __init__(self, usuario_id: int):
        self.usuario_id = usuario_id
    
    def obtener_miniaturas(self, limite: int = 10) -> list:
        """Obtiene miniaturas de imágenes de reportes"""
        # Simulación - en realidad consultaría la base de datos de reportes
        # from app.reporte.reporteColaborativo import ReporteColaborativo
        
        # Aquí iría la lógica real para obtener reportes con imágenes
        miniaturas = []
        contribuciones = ContribucionUsuario.objects.filter(
            usuario_id=self.usuario_id
        )[:limite]
        
        for contrib in contribuciones:
            # Simulación de obtener imagen del reporte
            miniatura = {
                'reporte_id': contrib.reporte_id,
                'imagen_url': f'/media/miniaturas/reporte_{contrib.reporte_id}.jpg',
                'fecha': contrib.fecha_contribucion
            }
            miniaturas.append(miniatura)
        
        return miniaturas


# 4. ESTILO PIPELINE (Procesamiento en cadena)
class PerfilDataPipeline:
    """Pipeline para procesar datos del perfil"""
    
    def __init__(self):
        self.steps = []
    
    def agregar_paso(self, step_function):
        """Agrega un paso al pipeline"""
        self.steps.append(step_function)
        return self
    
    def procesar(self, data):
        """Ejecuta todos los pasos del pipeline"""
        for step in self.steps:
            data = step(data)
        return data

# Pasos del pipeline
def validar_usuario_existe(data):
    """Paso 1: Validar que el usuario existe"""
    try:
        usuario = User.objects.get(id=data['usuario_id'])
        data['usuario'] = usuario
        return data
    except User.DoesNotExist:
        raise UsuarioNoEncontradoError(f"Usuario {data['usuario_id']} no encontrado")

def verificar_perfil_visible(data):
    """Paso 2: Verificar que el perfil es visible"""
    perfil_thing = PerfilUsuarioThing(data['usuario_id'])
    if not perfil_thing.es_visible():
        raise PerfilNoVisibleError("El perfil no es visible públicamente")
    data['perfil_thing'] = perfil_thing
    return data

def enriquecer_con_estadisticas(data):
    """Paso 3: Enriquecer con estadísticas"""
    data['estadisticas'] = data['perfil_thing'].obtener_estadisticas()
    return data

def agregar_miniaturas(data):
    """Paso 4: Agregar miniaturas de imágenes"""
    collector = ImagenMiniaturaCollector(data['usuario_id'])
    data['miniaturas'] = collector.obtener_miniaturas()
    return data

def formatear_respuesta(data):
    """Paso 5: Formatear respuesta final"""
    return {
        'usuario': {
            'id': data['usuario'].id,
            'username': data['usuario'].username,
            'nombre_completo': f"{data['usuario'].first_name} {data['usuario'].last_name}".strip()
        },
        'perfil': {
            'puntos_acumulados': data['estadisticas']['puntos_totales'],
            'total_reportes': data['estadisticas']['total_reportes'],
            'promedio_puntos': data['estadisticas']['promedio_puntos_por_reporte']
        },
        'contribuciones': data['estadisticas']['contribuciones_recientes'],
        'miniaturas': data['miniaturas']
    }


# 5. ESTILO RESTFUL (Views y Serializers)
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para el perfil de usuario"""
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = PerfilUsuario
        fields = [
            'usuario_username', 'nombre_completo', 'puntos_acumulados', 
            'total_reportes', 'perfil_visible', 'fecha_registro'
        ]
    
    def get_nombre_completo(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name}".strip()

class ContribucionSerializer(serializers.ModelSerializer):
    """Serializer para contribuciones"""
    class Meta:
        model = ContribucionUsuario
        fields = ['reporte_id', 'puntos_otorgados', 'fecha_contribucion', 'tipo_contribucion']

# API Views RESTful
@api_view(['GET'])
def perfil_publico(request, usuario_id):
    """
    GET /api/perfil/{usuario_id}/
    Obtiene el perfil público de un usuario
    """
    try:
        # Usar el pipeline para procesar la solicitud
        pipeline = PerfilDataPipeline()
        pipeline.agregar_paso(validar_usuario_existe) \
                .agregar_paso(verificar_perfil_visible) \
                .agregar_paso(enriquecer_con_estadisticas) \
                .agregar_paso(agregar_miniaturas) \
                .agregar_paso(formatear_respuesta)
        
        resultado = pipeline.procesar({'usuario_id': usuario_id})
        
        return Response(resultado, status=status.HTTP_200_OK)
        
    except UsuarioNoEncontradoError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except PerfilNoVisibleError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_403_FORBIDDEN
        )
    except Exception as e:
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def contribuciones_usuario(request, usuario_id):
    """
    GET /api/perfil/{usuario_id}/contribuciones/
    Obtiene las contribuciones de un usuario
    """
    try:
        perfil_thing = PerfilUsuarioThing(usuario_id)
        
        if not perfil_thing.es_visible():
            raise PerfilNoVisibleError("El perfil no es visible públicamente")
        
        contribuciones = perfil_thing.contribuciones
        serializer = ContribucionSerializer(contribuciones, many=True)
        
        return Response({
            'contribuciones': serializer.data,
            'total': len(contribuciones)
        }, status=status.HTTP_200_OK)
        
    except PerfilNoExisteError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except PerfilNoVisibleError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_403_FORBIDDEN
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cambiar_visibilidad_perfil(request):
    """
    PUT /api/perfil/visibilidad/
    Cambia la visibilidad del perfil del usuario autenticado
    """
    try:
        visible = request.data.get('visible', True)
        
        perfil_thing = PerfilUsuarioThing(request.user.id)
        perfil_thing.cambiar_visibilidad(visible)
        
        return Response({
            'mensaje': 'Visibilidad actualizada correctamente',
            'perfil_visible': visible
        }, status=status.HTTP_200_OK)
        
    except PerfilNoExisteError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Error al actualizar visibilidad'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 6. URLS CONFIGURATION
from django.urls import path

urlpatterns = [
    path('api/perfil/<int:usuario_id>/', perfil_publico, name='perfil_publico'),
    path('api/perfil/<int:usuario_id>/contribuciones/', contribuciones_usuario, name='contribuciones_usuario'),
    path('api/perfil/visibilidad/', cambiar_visibilidad_perfil, name='cambiar_visibilidad'),
]


# 7. MANAGEMENT COMMAND (Cookbook style)
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    """
    Comando para inicializar perfiles de usuario
    python manage.py inicializar_perfiles
    """
    help = 'Inicializa perfiles para usuarios existentes'
    
    def handle(self, *args, **options):
        """Cookbook: Receta para inicializar perfiles"""
        usuarios_sin_perfil = User.objects.filter(perfilusuario__isnull=True)
        
        for usuario in usuarios_sin_perfil:
            PerfilUsuario.objects.create(
                usuario=usuario,
                puntos_acumulados=0,
                total_reportes=0,
                perfil_visible=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Perfil creado para usuario: {usuario.username}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Proceso completado. {len(usuarios_sin_perfil)} perfiles creados.')
        )