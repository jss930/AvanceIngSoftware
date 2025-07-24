# ReportesUsuario.py - Refactorizado con principios de Clean Code

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import timedelta
from web.models import Reporte


# 1. PERSISTENT-TABLES (Models)
class InteraccionUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    reporte = models.ForeignKey(Reporte, on_delete=models.CASCADE)
    fecha_vista = models.DateTimeField(auto_now=True)
    tiempo_lectura_segundos = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'interaccion_usuario'
        unique_together = ['usuario', 'reporte']


class ConfiguracionUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    reportes_por_pagina = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(5), MaxValueValidator(50)]
    )
    mostrar_estadisticas = models.BooleanField(default=True)
    notificaciones_activas = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'configuracion_usuario'


# 2. ERROR/EXCEPTION HANDLING
class UsuarioReporteError(Exception):
    """Excepción base para errores relacionados con reportes de usuario"""
    pass


class UsuarioSinReportesError(UsuarioReporteError):
    """Excepción cuando el usuario no tiene reportes"""
    pass


class ConfiguracionInvalidaError(UsuarioReporteError):
    """Excepción para configuraciones inválidas"""
    pass


class PermisosInsuficientesError(UsuarioReporteError):
    """Excepción para permisos insuficientes"""
    pass


# 3. THINGS (Objetos con responsabilidades claras)
class EstadisticasUsuarioThing:    
    PERIODO_REPORTE_RECIENTE_DIAS = 7
    UMBRAL_USUARIO_ACTIVO = 5
    
    def __init__(self, usuario_id: int):
        self.usuario_id = usuario_id
        self._estadisticas_cache = None
    
    def obtener_estadisticas_completas(self):
        if self._estadisticas_cache is None:
            self._estadisticas_cache = self._calcular_estadisticas()
        return self._estadisticas_cache
    
    def _calcular_estadisticas(self):
        reportes = self._obtener_reportes_usuario()
        fecha_corte_reciente = timezone.now() - timedelta(days=self.PERIODO_REPORTE_RECIENTE_DIAS)
        
        return {
            'total_reportes': self._contar_reportes_totales(reportes),
            'reportes_validados': self._contar_reportes_validados(reportes),
            'reportes_recientes': self._contar_reportes_recientes(reportes, fecha_corte_reciente),
            'tasa_validacion': self._calcular_tasa_validacion(reportes),
            'promedio_credibilidad': self._calcular_promedio_credibilidad(reportes),
            'es_usuario_activo': self._determinar_usuario_activo(reportes),
            'tipos_reportes_frecuentes': self._obtener_tipos_frecuentes(reportes)
        }
    
    def _obtener_reportes_usuario(self):
        return Reporte.objects.filter(usuario_reportador_id=self.usuario_id)
    
    def _contar_reportes_totales(self, reportes):
        return reportes.count()
    
    def _contar_reportes_validados(self, reportes):
        return reportes.filter(es_validado=True).count()
    
    def _contar_reportes_recientes(self, reportes, fecha_corte):
        return reportes.filter(fecha_creacion__gte=fecha_corte).count()
    
    def _calcular_tasa_validacion(self, reportes):
        total = reportes.count()
        validados = reportes.filter(es_validado=True).count()
        return (validados / total * 100) if total > 0 else 0.0
    
    def _calcular_promedio_credibilidad(self, reportes):
        credibilidades = []
        for reporte in reportes:
            total_votos = reporte.votos_positivos + reporte.votos_negativos
            if total_votos > 0:
                credibilidad = (reporte.votos_positivos / total_votos) * 100
                credibilidades.append(credibilidad)
        
        return sum(credibilidades) / len(credibilidades) if credibilidades else 0.0
    
    def _determinar_usuario_activo(self, reportes):
        fecha_corte = timezone.now() - timedelta(days=self.PERIODO_REPORTE_RECIENTE_DIAS)
        reportes_recientes = reportes.filter(fecha_creacion__gte=fecha_corte).count()
        return reportes_recientes >= self.UMBRAL_USUARIO_ACTIVO
    
    def _obtener_tipos_frecuentes(self, reportes):
        from django.db.models import Count
        return list(reportes.values('tipo_incidente').annotate(
            cantidad=Count('tipo_incidente')
        ).order_by('-cantidad')[:3])


class FiltroReportesThing:    
    ESTADOS_VALIDOS = ['pendiente', 'validado', 'archivado']
    
    def __init__(self, reportes_queryset):
        self.reportes = reportes_queryset
    
    def aplicar_filtros(self, filtros: dict):
        reportes_filtrados = self.reportes
        
        reportes_filtrados = self._filtrar_por_estado(reportes_filtrados, filtros.get('estado'))
        reportes_filtrados = self._filtrar_por_tipo(reportes_filtrados, filtros.get('tipo_incidente'))
        reportes_filtrados = self._filtrar_por_fecha(reportes_filtrados, filtros.get('fecha_desde'))
        reportes_filtrados = self._filtrar_por_nivel_peligro(reportes_filtrados, filtros.get('nivel_peligro'))
        reportes_filtrados = self._filtrar_por_validacion(reportes_filtrados, filtros.get('solo_validados'))
        
        return reportes_filtrados
    
    def _filtrar_por_estado(self, queryset, estado):
        if estado and estado in self.ESTADOS_VALIDOS:
            return queryset.filter(estado_reporte=estado)
        return queryset
    
    def _filtrar_por_tipo(self, queryset, tipo_incidente):
        if tipo_incidente:
            return queryset.filter(tipo_incidente=tipo_incidente)
        return queryset
    
    def _filtrar_por_fecha(self, queryset, fecha_desde):
        if fecha_desde:
            return queryset.filter(fecha_creacion__gte=fecha_desde)
        return queryset
    
    def _filtrar_por_nivel_peligro(self, queryset, nivel_peligro):
        if nivel_peligro:
            return queryset.filter(nivel_peligro=nivel_peligro)
        return queryset
    
    def _filtrar_por_validacion(self, queryset, solo_validados):
        if solo_validados:
            return queryset.filter(es_validado=True)
        return queryset


class ConfiguracionUsuarioThing:    
    REPORTES_POR_PAGINA_DEFAULT = 10
    
    def __init__(self, usuario_id: int):
        self.usuario_id = usuario_id
        self._configuracion = None
    
    def obtener_configuracion(self):
        if self._configuracion is None:
            self._configuracion, created = ConfiguracionUsuario.objects.get_or_create(
                usuario_id=self.usuario_id,
                defaults={
                    'reportes_por_pagina': self.REPORTES_POR_PAGINA_DEFAULT,
                    'mostrar_estadisticas': True,
                    'notificaciones_activas': True
                }
            )
        return self._configuracion
    
    def actualizar_configuracion(self, nuevos_datos: dict):
        configuracion = self.obtener_configuracion()
        
        self._validar_datos_configuracion(nuevos_datos)
        
        for campo, valor in nuevos_datos.items():
            if hasattr(configuracion, campo):
                setattr(configuracion, campo, valor)
        
        configuracion.save()
        self._configuracion = configuracion
        return configuracion
    
    def _validar_datos_configuracion(self, datos: dict):
        if 'reportes_por_pagina' in datos:
            reportes_por_pagina = datos['reportes_por_pagina']
            if not (5 <= reportes_por_pagina <= 50):
                raise ConfiguracionInvalidaError("Los reportes por página deben estar entre 5 y 50")


# 4. PIPELINE (Procesamiento en cadena)
class ReportesUsuarioPipeline:    
    def __init__(self):
        self.pasos = []
    
    def agregar_paso(self, paso_funcion):
        self.pasos.append(paso_funcion)
        return self
    
    def ejecutar(self, datos_iniciales: dict):
        datos = datos_iniciales.copy()
        
        for paso in self.pasos:
            datos = paso(datos)
            
        return datos


# Pasos del pipeline
def validar_usuario_existe(datos: dict):
    try:
        usuario = User.objects.get(id=datos['usuario_id'])
        datos['usuario'] = usuario
        return datos
    except User.DoesNotExist:
        raise UsuarioReporteError(f"Usuario {datos['usuario_id']} no encontrado")


def cargar_configuracion_usuario(datos: dict):
    config_thing = ConfiguracionUsuarioThing(datos['usuario_id'])
    datos['configuracion'] = config_thing.obtener_configuracion()
    return datos


def cargar_reportes_usuario(datos: dict):
    reportes = Reporte.objects.filter(
        usuario_reportador_id=datos['usuario_id']
    ).select_related('usuario_reportador').order_by('-fecha_creacion')
    
    if not reportes.exists():
        raise UsuarioSinReportesError("El usuario no tiene reportes")
    
    datos['reportes_base'] = reportes
    return datos


def aplicar_filtros_reportes(datos: dict):
    filtro_thing = FiltroReportesThing(datos['reportes_base'])
    filtros = datos.get('filtros', {})
    
    datos['reportes_filtrados'] = filtro_thing.aplicar_filtros(filtros)
    return datos


def calcular_estadisticas_usuario(datos: dict):
    stats_thing = EstadisticasUsuarioThing(datos['usuario_id'])
    datos['estadisticas'] = stats_thing.obtener_estadisticas_completas()
    return datos


def aplicar_paginacion(datos: dict):
    reportes = datos['reportes_filtrados']
    reportes_por_pagina = datos['configuracion'].reportes_por_pagina
    pagina_actual = datos.get('pagina', 1)
    
    paginator = Paginator(reportes, reportes_por_pagina)
    page_obj = paginator.get_page(pagina_actual)
    
    datos['reportes_paginados'] = page_obj
    datos['info_paginacion'] = {
        'pagina_actual': page_obj.number,
        'total_paginas': paginator.num_pages,
        'tiene_anterior': page_obj.has_previous(),
        'tiene_siguiente': page_obj.has_next(),
        'total_reportes': paginator.count
    }
    return datos


def formatear_respuesta_web(datos: dict):
    return {
        'usuario': datos['usuario'],
        'reportes': datos['reportes_paginados'],
        'estadisticas': datos['estadisticas'] if datos['configuracion'].mostrar_estadisticas else None,
        'configuracion': datos['configuracion'],
        'info_paginacion': datos['info_paginacion'],
        'filtros_aplicados': datos.get('filtros', {})
    }


def formatear_respuesta_api(datos: dict):
    reportes_serializados = []
    
    for reporte in datos['reportes_paginados']:
        total_votos = reporte.votos_positivos + reporte.votos_negativos
        credibilidad = (reporte.votos_positivos / total_votos * 100) if total_votos > 0 else 0
        
        reportes_serializados.append({
            'id': reporte.id,
            'titulo': reporte.titulo,
            'descripcion_corta': reporte.descripcion[:100] + '...' if len(reporte.descripcion) > 100 else reporte.descripcion,
            'tipo_incidente': reporte.get_tipo_incidente_display(),
            'estado': reporte.get_estado_reporte_display(),
            'nivel_peligro': reporte.nivel_peligro,
            'fecha_creacion': reporte.fecha_creacion.isoformat(),
            'credibilidad': round(credibilidad, 2),
            'es_validado': reporte.es_validado,
            'tiene_imagen': bool(reporte.imagen_geolocalizada)
        })
    
    return {
        'usuario': {
            'id': datos['usuario'].id,
            'username': datos['usuario'].username,
            'nombre_completo': f"{datos['usuario'].first_name} {datos['usuario'].last_name}".strip()
        },
        'reportes': reportes_serializados,
        'estadisticas': datos['estadisticas'],
        'paginacion': datos['info_paginacion'],
        'configuracion': {
            'reportes_por_pagina': datos['configuracion'].reportes_por_pagina,
            'mostrar_estadisticas': datos['configuracion'].mostrar_estadisticas
        }
    }


# 5. RESTFUL (Views y Serializers)
class ConfiguracionUsuarioSerializer(serializers.ModelSerializer):    
    class Meta:
        model = ConfiguracionUsuario
        fields = ['reportes_por_pagina', 'mostrar_estadisticas', 'notificaciones_activas']
    
    def validate_reportes_por_pagina(self, value):
        if not (5 <= value <= 50):
            raise serializers.ValidationError("Debe estar entre 5 y 50")
        return value


# Views Django tradicionales
@login_required
def vista_reportes_usuario(request):
    try:
        # Construir pipeline
        pipeline = ReportesUsuarioPipeline()
        pipeline.agregar_paso(validar_usuario_existe) \
                .agregar_paso(cargar_configuracion_usuario) \
                .agregar_paso(cargar_reportes_usuario) \
                .agregar_paso(aplicar_filtros_reportes) \
                .agregar_paso(calcular_estadisticas_usuario) \
                .agregar_paso(aplicar_paginacion) \
                .agregar_paso(formatear_respuesta_web)
        
        # Preparar datos iniciales
        filtros = {
            'estado': request.GET.get('estado'),
            'tipo_incidente': request.GET.get('tipo'),
            'fecha_desde': request.GET.get('fecha_desde'),
            'nivel_peligro': request.GET.get('nivel_peligro'),
            'solo_validados': request.GET.get('solo_validados') == 'true'
        }
        
        datos_iniciales = {
            'usuario_id': request.user.id,
            'filtros': {k: v for k, v in filtros.items() if v},
            'pagina': request.GET.get('page', 1)
        }
        
        # Ejecutar pipeline
        resultado = pipeline.ejecutar(datos_iniciales)
        
        # Agregar datos adicionales para el template
        resultado.update({
            'tipos_incidente': Reporte.TIPOS_INCIDENTE,
            'estados_reporte': Reporte.ESTADOS_REPORTE,
            'niveles_peligro': range(1, 6)  # Asumiendo niveles 1-5
        })
        
        return render(request, 'reportes/usuario_reportes.html', resultado)
        
    except UsuarioSinReportesError:
        context = {
            'mensaje_info': 'No tienes reportes creados aún.',
            'mostrar_boton_crear': True
        }
        return render(request, 'reportes/sin_reportes.html', context)
    
    except Exception as e:
        context = {
            'error': 'Error al cargar tus reportes. Intenta de nuevo.',
            'detalle_error': str(e) if settings.DEBUG else None
        }
        return render(request, 'reportes/error.html', context)


@login_required
def vista_configuracion_usuario(request):
    config_thing = ConfiguracionUsuarioThing(request.user.id)
    
    if request.method == 'POST':
        try:
            nuevos_datos = {
                'reportes_por_pagina': int(request.POST.get('reportes_por_pagina', 10)),
                'mostrar_estadisticas': request.POST.get('mostrar_estadisticas') == 'on',
                'notificaciones_activas': request.POST.get('notificaciones_activas') == 'on'
            }
            
            configuracion = config_thing.actualizar_configuracion(nuevos_datos)
            
            context = {
                'configuracion': configuracion,
                'mensaje_exito': 'Configuración actualizada correctamente'
            }
            
        except ConfiguracionInvalidaError as e:
            context = {
                'configuracion': config_thing.obtener_configuracion(),
                'error': str(e)
            }
    else:
        context = {
            'configuracion': config_thing.obtener_configuracion()
        }
    
    return render(request, 'reportes/configuracion_usuario.html', context)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_reportes_usuario(request):
    """
    GET /api/mis-reportes/
    Obtiene los reportes del usuario autenticado
    """
    try:
        pipeline = ReportesUsuarioPipeline()
        pipeline.agregar_paso(validar_usuario_existe) \
                .agregar_paso(cargar_configuracion_usuario) \
                .agregar_paso(cargar_reportes_usuario) \
                .agregar_paso(aplicar_filtros_reportes) \
                .agregar_paso(calcular_estadisticas_usuario) \
                .agregar_paso(aplicar_paginacion) \
                .agregar_paso(formatear_respuesta_api)
        
        # Obtener filtros de query parameters
        filtros = {
            'estado': request.GET.get('estado'),
            'tipo_incidente': request.GET.get('tipo'),
            'fecha_desde': request.GET.get('fecha_desde'),
            'nivel_peligro': request.GET.get('nivel_peligro'),
            'solo_validados': request.GET.get('solo_validados') == 'true'
        }
        
        datos_iniciales = {
            'usuario_id': request.user.id,
            'filtros': {k: v for k, v in filtros.items() if v},
            'pagina': request.GET.get('page', 1)
        }
        
        resultado = pipeline.ejecutar(datos_iniciales)
        return Response(resultado, status=status.HTTP_200_OK)
        
    except UsuarioSinReportesError:
        return Response(
            {
                'mensaje': 'No tienes reportes creados',
                'reportes': [],
                'estadisticas': None
            },
            status=status.HTTP_200_OK
        )
    
    except UsuarioReporteError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception as e:
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def api_configuracion_usuario(request):
    """
    GET/PUT /api/mi-configuracion/
    Obtiene o actualiza la configuración del usuario
    """
    config_thing = ConfiguracionUsuarioThing(request.user.id)
    
    if request.method == 'GET':
        configuracion = config_thing.obtener_configuracion()
        serializer = ConfiguracionUsuarioSerializer(configuracion)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        try:
            serializer = ConfiguracionUsuarioSerializer(data=request.data)
            if serializer.is_valid():
                configuracion = config_thing.actualizar_configuracion(serializer.validated_data)
                response_serializer = ConfiguracionUsuarioSerializer(configuracion)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except ConfiguracionInvalidaError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_estadisticas_usuario(request):
    """
    GET /api/mis-estadisticas/
    Obtiene las estadísticas del usuario
    """
    try:
        stats_thing = EstadisticasUsuarioThing(request.user.id)
        estadisticas = stats_thing.obtener_estadisticas_completas()
        
        return Response(estadisticas, status=status.HTTP_200_OK)
        
    except Exception:
        return Response(
            {'error': 'Error al calcular estadísticas'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# 6. URLS Configuration
from django.urls import path

app_name = 'reportes_usuario'

urlpatterns = [
    # Views tradicionales
    path('mis-reportes/', vista_reportes_usuario, name='lista_reportes'),
    path('configuracion/', vista_configuracion_usuario, name='configuracion'),
    
    # API endpoints
    path('api/mis-reportes/', api_reportes_usuario, name='api_lista_reportes'),
    path('api/mi-configuracion/', api_configuracion_usuario, name='api_configuracion'),
    path('api/mis-estadisticas/', api_estadisticas_usuario, name='api_estadisticas'),
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
