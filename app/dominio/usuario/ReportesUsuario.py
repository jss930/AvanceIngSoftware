# 1. ESTILO PERSISTENT-TABLES (Models)
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from web.models import Reporte

class VotoReporte(models.Model):
    """Modelo para almacenar votos de validación"""
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE, related_name='votos')
    usuario_votante = models.ForeignKey(User, on_delete=models.CASCADE)
    voto_positivo = models.BooleanField()
    fecha_voto = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'voto_reporte'
        unique_together = ['reporte', 'usuario_votante']


# 2. ESTILO ERROR/EXCEPTION HANDLING
class ReporteError(Exception):
    """Excepción base para errores de reporte"""
    pass

class ReporteNoEncontradoError(ReporteError):
    """Excepción cuando el reporte no existe"""
    pass

class SinPermisosReporteError(ReporteError):
    """Excepción cuando el usuario no tiene permisos"""
    pass

class ReporteNoEditableError(ReporteError):
    """Excepción cuando el reporte no puede ser editado"""
    pass


# 3. ESTILO THINGS (Objetos con responsabilidades claras)
class ReporteVisualizadorThing:
    """Maneja la visualización de reportes de un usuario"""
    
    def __init__(self, usuario_id: int):
        self.usuario_id = usuario_id
        self._reportes = None
        self._estadisticas = None
    
    @property
    def reportes(self):
        """Lazy loading de reportes"""
        if self._reportes is None:
            self._reportes = Reporte.objects.filter(
                usuario_reportador_id=self.usuario_id
            ).order_by('-fecha_creacion')
        return self._reportes
    
    def obtener_reportes_por_estado(self, estado: str = None):
        """Obtiene reportes filtrados por estado"""
        queryset = self.reportes
        if estado:
            queryset = queryset.filter(estado_reporte=estado)
        return queryset
    
    def obtener_reportes_recientes(self, limite: int = 5):
        """Obtiene los reportes más recientes"""
        return self.reportes[:limite]
    
    def obtener_estadisticas_usuario(self):
        """Calcula estadísticas del usuario"""
        if self._estadisticas is None:
            total_reportes = self.reportes.count()
            reportes_validados = self.reportes.filter(es_validado=True).count()
            reportes_pendientes = self.reportes.filter(estado_reporte='pendiente').count()
            promedio_votos = self.reportes.aggregate(
                promedio_positivos=models.Avg('votos_positivos'),
                promedio_negativos=models.Avg('votos_negativos')
            )
            
            self._estadisticas = {
                'total_reportes': total_reportes,
                'reportes_validados': reportes_validados,
                'reportes_pendientes': reportes_pendientes,
                'tasa_validacion': (reportes_validados / total_reportes * 100) if total_reportes > 0 else 0,
                'promedio_votos_positivos': promedio_votos['promedio_positivos'] or 0,
                'promedio_votos_negativos': promedio_votos['promedio_negativos'] or 0,
            }
        return self._estadisticas


class ReporteDetalleThing:
    """Maneja los detalles de un reporte específico"""
    
    def __init__(self, reporte_id: int):
        self.reporte_id = reporte_id
        self._reporte = None
    
    @property
    def reporte(self):
        """Lazy loading del reporte"""
        if self._reporte is None:
            try:
                self._reporte = Reporte.objects.select_related('usuario_reportador').get(
                    id=self.reporte_id
                )
            except Reporte.DoesNotExist:
                raise ReporteNoEncontradoError(f"Reporte {self.reporte_id} no encontrado")
        return self._reporte
    
    def obtener_detalles_completos(self):
        """Obtiene todos los detalles del reporte"""
        reporte = self.reporte
        votos = VotoReporte.objects.filter(reporte=reporte)
        
        return {
            'reporte': reporte,
            'credibilidad': self._calcular_credibilidad(),
            'total_votos': votos.count(),
            'votos_detalle': votos.select_related('usuario_votante'),
            'puede_editar': self._puede_ser_editado(),
            'es_reciente': self._es_reporte_reciente(),
            'ubicacion_texto': self._obtener_ubicacion_texto()
        }
    
    def _calcular_credibilidad(self) -> float:
        """Calcula la credibilidad del reporte"""
        reporte = self.reporte
        total = reporte.votos_positivos + reporte.votos_negativos
        return (reporte.votos_positivos / total * 100) if total > 0 else 0.0
    
    def _puede_ser_editado(self) -> bool:
        """Verifica si el reporte puede ser editado"""
        return self.reporte.estado_reporte == 'pendiente'
    
    def _es_reporte_reciente(self) -> bool:
        """Verifica si el reporte es reciente (menos de 24 horas)"""
        return (timezone.now() - self.reporte.fecha_creacion).days < 1
    
    def _obtener_ubicacion_texto(self) -> str:
        """Convierte coordenadas a texto legible"""
        # Aquí podrías integrar con un servicio de geocodificación
        return f"Lat: {self.reporte.latitud}, Lng: {self.reporte.longitud}"


# 4. ESTILO PIPELINE (Procesamiento en cadena)
class ReportesDataPipeline:
    """Pipeline para procesar datos de reportes"""
    
    def __init__(self):
        self.steps = []
    
    def agregar_paso(self, step_function):
        self.steps.append(step_function)
        return self
    
    def procesar(self, data):
        """Ejecuta todos los pasos del pipeline"""
        for step in self.steps:
            data = step(data)
        return data

# Pasos del pipeline
def validar_usuario_reportes(data):
    """Valida que el usuario tenga acceso a ver reportes"""
    try:
        usuario = User.objects.get(id=data['usuario_id'])
        data['usuario'] = usuario
        return data
    except User.DoesNotExist:
        raise ReporteError(f"Usuario {data['usuario_id']} no encontrado")

def cargar_reportes_usuario(data):
    """Carga los reportes del usuario"""
    visualizador = ReporteVisualizadorThing(data['usuario_id'])
    data['visualizador'] = visualizador
    data['reportes'] = visualizador.reportes
    return data

def aplicar_filtros(data):
    """Aplica filtros según los parámetros"""
    filtros = data.get('filtros', {})
    reportes = data['reportes']
    
    if filtros.get('estado'):
        reportes = reportes.filter(estado_reporte=filtros['estado'])
    
    if filtros.get('tipo_incidente'):
        reportes = reportes.filter(tipo_incidente=filtros['tipo_incidente'])
    
    if filtros.get('fecha_desde'):
        reportes = reportes.filter(fecha_creacion__gte=filtros['fecha_desde'])
    
    data['reportes_filtrados'] = reportes
    return data

def cargar_estadisticas(data):
    """Carga estadísticas del usuario"""
    data['estadisticas'] = data['visualizador'].obtener_estadisticas_usuario()
    return data

def formatear_respuesta_reportes(data):
    """Formatea la respuesta final"""
    reportes_data = []
    for reporte in data['reportes_filtrados']:
        reportes_data.append({
            'id': reporte.id,
            'titulo': reporte.titulo,
            'descripcion': reporte.descripcion[:100] + '...' if len(reporte.descripcion) > 100 else reporte.descripcion,
            'tipo_incidente': reporte.get_tipo_incidente_display(),
            'estado': reporte.get_estado_reporte_display(),
            'nivel_peligro': reporte.nivel_peligro,
            'fecha_creacion': reporte.fecha_creacion,
            'votos_positivos': reporte.votos_positivos,
            'votos_negativos': reporte.votos_negativos,
            'credibilidad': (reporte.votos_positivos / (reporte.votos_positivos + reporte.votos_negativos) * 100) if (reporte.votos_positivos + reporte.votos_negativos) > 0 else 0,
            'tiene_imagen': bool(reporte.imagen_geolocalizada),
            'es_validado': reporte.es_validado
        })
    
    return {
        'usuario': {
            'id': data['usuario'].id,
            'username': data['usuario'].username,
            'nombre_completo': f"{data['usuario'].first_name} {data['usuario'].last_name}".strip()
        },
        'estadisticas': data['estadisticas'],
        'reportes': reportes_data,
        'total_reportes': len(reportes_data)
    }


# 5. ESTILO RESTFUL (Views y Serializers)
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator

class ReporteSerializer(serializers.ModelSerializer):
    tipo_incidente_display = serializers.CharField(source='get_tipo_incidente_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_reporte_display', read_only=True)
    usuario_reportador_username = serializers.CharField(source='usuario_reportador.username', read_only=True)
    credibilidad = serializers.SerializerMethodField()
    
    class Meta:
        model = Reporte
        fields = [
            'id', 'titulo', 'descripcion', 'tipo_incidente', 'tipo_incidente_display',
            'estado_reporte', 'estado_display', 'nivel_peligro', 'fecha_creacion',
            'fecha_actualizacion', 'votos_positivos', 'votos_negativos',
            'usuario_reportador_username', 'credibilidad', 'es_validado',
            'latitud', 'longitud', 'imagen_geolocalizada'
        ]
    
    def get_credibilidad(self, obj):
        total = obj.votos_positivos + obj.votos_negativos
        return (obj.votos_positivos / total * 100) if total > 0 else 0

# Views Django tradicionales
@login_required
def mis_reportes_view(request):
    """Vista principal para mostrar los reportes del usuario"""
    try:
        # Usar pipeline para procesar la solicitud
        pipeline = ReportesDataPipeline()
        pipeline.agregar_paso(validar_usuario_reportes) \
                .agregar_paso(cargar_reportes_usuario) \
                .agregar_paso(aplicar_filtros) \
                .agregar_paso(cargar_estadisticas)
        
        # Obtener filtros de la URL
        filtros = {
            'estado': request.GET.get('estado'),
            'tipo_incidente': request.GET.get('tipo'),
            'fecha_desde': request.GET.get('fecha_desde')
        }
        
        data = {
            'usuario_id': request.user.id,
            'filtros': {k: v for k, v in filtros.items() if v}
        }
        
        resultado = pipeline.procesar(data)
        
        # Paginación
        paginator = Paginator(resultado['reportes_filtrados'], 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'reportes': page_obj,
            'estadisticas': resultado['estadisticas'],
            'filtros_aplicados': filtros,
            'tipos_incidente': Reporte.TIPOS_INCIDENTE,
            'estados_reporte': Reporte.ESTADOS_REPORTE,
        }
        
        return render(request, 'reportes/mis_reportes.html', context)
        
    except Exception:
        context = {
            'error': 'Error al cargar los reportes',
            'reportes': [],
            'estadisticas': {}
        }
        return render(request, 'reportes/mis_reportes.html', context)

@login_required
def detalle_reporte_view(request, reporte_id):
    """Vista para mostrar el detalle de un reporte"""
    try:
        detalle_thing = ReporteDetalleThing(reporte_id)
        detalles = detalle_thing.obtener_detalles_completos()
        
        # Verificar permisos
        if detalles['reporte'].usuario_reportador != request.user:
            raise SinPermisosReporteError("No tienes permisos para ver este reporte")
        
        context = {
            'reporte': detalles['reporte'],
            'credibilidad': detalles['credibilidad'],
            'total_votos': detalles['total_votos'],
            'puede_editar': detalles['puede_editar'],
            'es_reciente': detalles['es_reciente'],
            'ubicacion_texto': detalles['ubicacion_texto']
        }
        
        return render(request, 'reportes/detalle_reporte.html', context)
        
    except ReporteNoEncontradoError:
        context = {'error': 'Reporte no encontrado'}
        return render(request, 'reportes/error.html', context, status=404)
    except SinPermisosReporteError:
        context = {'error': 'No tienes permisos para ver este reporte'}
        return render(request, 'reportes/error.html', context, status=403)

# API Views RESTful
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_mis_reportes(request):
    """
    GET /api/mis-reportes/
    Obtiene los reportes del usuario autenticado via API
    """
    try:
        pipeline = ReportesDataPipeline()
        pipeline.agregar_paso(validar_usuario_reportes) \
                .agregar_paso(cargar_reportes_usuario) \
                .agregar_paso(aplicar_filtros) \
                .agregar_paso(cargar_estadisticas) \
                .agregar_paso(formatear_respuesta_reportes)
        
        # Obtener filtros de los query parameters
        filtros = {
            'estado': request.GET.get('estado'),
            'tipo_incidente': request.GET.get('tipo'),
            'fecha_desde': request.GET.get('fecha_desde')
        }
        
        data = {
            'usuario_id': request.user.id,
            'filtros': {k: v for k, v in filtros.items() if v}
        }
        
        resultado = pipeline.procesar(data)
        return Response(resultado, status=status.HTTP_200_OK)
        
    except Exception:
        return Response(
            {'error': 'Error al obtener reportes'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_detalle_reporte(request, reporte_id):
    """
    GET /api/reporte/{id}/
    Obtiene el detalle de un reporte específico
    """
    try:
        detalle_thing = ReporteDetalleThing(reporte_id)
        reporte = detalle_thing.reporte
        
        # Verificar permisos
        if reporte.usuario_reportador != request.user:
            raise SinPermisosReporteError("No tienes permisos para ver este reporte")
        
        detalles = detalle_thing.obtener_detalles_completos()
        serializer = ReporteSerializer(reporte)
        
        return Response({
            'reporte': serializer.data,
            'credibilidad': detalles['credibilidad'],
            'puede_editar': detalles['puede_editar'],
            'es_reciente': detalles['es_reciente'],
            'ubicacion_texto': detalles['ubicacion_texto']
        }, status=status.HTTP_200_OK)
        
    except ReporteNoEncontradoError:
        return Response(
            {'error': 'Reporte no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except SinPermisosReporteError:
        return Response(
            {'error': 'No tienes permisos para ver este reporte'},
            status=status.HTTP_403_FORBIDDEN
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_estadisticas_usuario(request):
    """
    GET /api/mis-estadisticas/
    Obtiene estadísticas del usuario
    """
    try:
        visualizador = ReporteVisualizadorThing(request.user.id)
        estadisticas = visualizador.obtener_estadisticas_usuario()
        
        return Response(estadisticas, status=status.HTTP_200_OK)
        
    except Exception:
        return Response(
            {'error': 'Error al obtener estadísticas'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 6. URLS CONFIGURATION
from django.urls import path

urlpatterns = [
    # Views tradicionales
    path('mis-reportes/', mis_reportes_view, name='mis_reportes'),
    path('reporte/<int:reporte_id>/', detalle_reporte_view, name='detalle_reporte'),
    
    # API endpoints
    path('api/mis-reportes/', api_mis_reportes, name='api_mis_reportes'),
    path('api/reporte/<int:reporte_id>/', api_detalle_reporte, name='api_detalle_reporte'),
    path('api/mis-estadisticas/', api_estadisticas_usuario, name='api_estadisticas_usuario'),
]


# 7. MANAGEMENT COMMAND (Cookbook style)
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    """
    Comando para limpiar reportes antiguos
    python manage.py limpiar_reportes_antiguos --dias=30
    """
    help = 'Limpia reportes más antiguos que X días'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Número de días para considerar reportes como antiguos'
        )
    
    def handle(self, *args, **options):
        dias = options['dias']
        fecha_limite = timezone.now() - timedelta(days=dias)
        
        reportes_antiguos = Reporte.objects.filter(
            fecha_creacion__lt=fecha_limite,
            estado_reporte='archivado'
        )
        
        cantidad = reportes_antiguos.count()
        reportes_antiguos.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Se eliminaron {cantidad} reportes antiguos (más de {dias} días)')
        )