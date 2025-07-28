# web/services/reportes_usuario_service.py

from django.db import models
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from web.models import ReporteColaborativo, ConfiguracionUsuario, InteraccionUsuario



# Excepciones personalizadas
class UsuarioReporteError(Exception):
    """Excepción base para errores relacionados con reportes de usuario"""
    pass


class UsuarioSinReportesError(UsuarioReporteError):
    """Excepción cuando el usuario no tiene reportes"""
    pass


class ConfiguracionInvalidaError(UsuarioReporteError):
    """Excepción para configuraciones inválidas"""
    pass


# Servicios principales
class EstadisticasUsuarioService:    
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
            'reportes_pendientes': self._contar_reportes_pendientes(reportes),
            'reportes_recientes': self._contar_reportes_recientes(reportes, fecha_corte_reciente),
            'tasa_validacion': self._calcular_tasa_validacion(reportes),
            'promedio_credibilidad': self._calcular_promedio_credibilidad(reportes),
            'es_usuario_activo': self._determinar_usuario_activo(reportes),
            'tipos_reportes_frecuentes': self._obtener_tipos_frecuentes(reportes)
        }
    
    def _obtener_reportes_usuario(self):
        return ReporteColaborativo.objects.filter(usuario_reportador_id=self.usuario_id)
    
    def _contar_reportes_totales(self, reportes):
        return reportes.count()
    
    def _contar_reportes_validados(self, reportes):
        return reportes.filter(es_validado=True).count()
    
    def _contar_reportes_pendientes(self, reportes):
        return reportes.filter(estado_reporte='pendiente').count()
    
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


class FiltroReportesService:    
    ESTADOS_VALIDOS = ['pendiente', 'validado', 'rechazado', 'archivado']
    
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


class ConfiguracionUsuarioService:    
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


class ReportesUsuarioService:    
    def __init__(self, usuario_id: int):
        self.usuario_id = usuario_id
        self.pipeline = ReportesUsuarioPipeline()
        self._configurar_pipeline()
    
    def _configurar_pipeline(self):
        self.pipeline.agregar_paso(self._validar_usuario_existe)
        self.pipeline.agregar_paso(self._cargar_configuracion_usuario)
        self.pipeline.agregar_paso(self._cargar_reportes_usuario)
        self.pipeline.agregar_paso(self._aplicar_filtros_reportes)
        self.pipeline.agregar_paso(self._calcular_estadisticas_usuario)
        self.pipeline.agregar_paso(self._agregar_credibilidad_reportes)
        self.pipeline.agregar_paso(self._aplicar_paginacion)
    
    def obtener_reportes_usuario(self, filtros: dict = None, pagina: int = 1):
        datos_iniciales = {
            'usuario_id': self.usuario_id,
            'filtros': filtros or {},
            'pagina': pagina
        }
        
        return self.pipeline.ejecutar(datos_iniciales)
    
    # Pasos del pipeline como métodos privados
    def _validar_usuario_existe(self, datos: dict):
        try:
            usuario = User.objects.get(id=datos['usuario_id'])
            datos['usuario'] = usuario
            return datos
        except User.DoesNotExist:
            raise UsuarioReporteError(f"Usuario {datos['usuario_id']} no encontrado")

    def obtener_reportes_recientes(self, limite: int = 5):
        pipeline_recientes = ReportesUsuarioPipeline()
        pipeline_recientes.agregar_paso(self._validar_usuario_existe)
        pipeline_recientes.agregar_paso(self._cargar_reportes_recientes)
        
        datos_iniciales = {
            'usuario_id': self.usuario_id,
            'limite': limite
        }
        
        resultado = pipeline_recientes.ejecutar(datos_iniciales)
        return resultado['reportes_recientes']
    
    def _cargar_reportes_recientes(self, datos: dict):
        limite = datos.get('limite', 5)
        reportes = ReporteColaborativo.objects.filter(
            usuario_reportador_id=datos['usuario_id']
        ).select_related('usuario_reportador').order_by('-fecha_creacion')[:limite]
        
        datos['reportes_recientes'] = list(reportes)
        return datos
    
    def _cargar_configuracion_usuario(self, datos: dict):
        config_service = ConfiguracionUsuarioService(datos['usuario_id'])
        datos['configuracion'] = config_service.obtener_configuracion()
        return datos
    
    def _cargar_reportes_usuario(self, datos: dict):
        reportes = ReporteColaborativo.objects.filter(
            usuario_reportador_id=datos['usuario_id']
        ).select_related('usuario_reportador').order_by('-fecha_creacion')
        
        if not reportes.exists():
            raise UsuarioSinReportesError("El usuario no tiene reportes")
        
        datos['reportes_base'] = reportes
        return datos
    
    def _aplicar_filtros_reportes(self, datos: dict):
        if datos['filtros']:
            filtro_service = FiltroReportesService(datos['reportes_base'])
            datos['reportes_filtrados'] = filtro_service.aplicar_filtros(datos['filtros'])
        else:
            datos['reportes_filtrados'] = datos['reportes_base']
        return datos
    
    def _calcular_estadisticas_usuario(self, datos: dict):
        stats_service = EstadisticasUsuarioService(datos['usuario_id'])
        datos['estadisticas'] = stats_service.obtener_estadisticas_completas()
        return datos
    
    def _agregar_credibilidad_reportes(self, datos: dict):
        reportes_con_credibilidad = []
        
        for reporte in datos['reportes_filtrados']:
            total_votos = reporte.votos_positivos + reporte.votos_negativos
            if total_votos > 0:
                reporte.credibilidad_porcentaje = round((reporte.votos_positivos * 100) / total_votos)
                reporte.credibilidad_width = reporte.credibilidad_porcentaje
            else:
                reporte.credibilidad_porcentaje = 0
                reporte.credibilidad_width = 0
            reporte.total_votos = total_votos
            reportes_con_credibilidad.append(reporte)
        
        datos['reportes_procesados'] = reportes_con_credibilidad
        return datos
    
    def _aplicar_paginacion(self, datos: dict):
        reportes = datos['reportes_procesados']
        reportes_por_pagina = datos['configuracion'].reportes_por_pagina
        pagina_actual = datos.get('pagina', 1)
        
        paginator = Paginator(reportes, reportes_por_pagina)
        page_obj = paginator.get_page(pagina_actual)
        
        return {
            'usuario': datos['usuario'],
            'reportes': page_obj,
            'estadisticas': datos['estadisticas'] if datos['configuracion'].mostrar_estadisticas else None,
            'configuracion': datos['configuracion'],
            'info_paginacion': {
                'pagina_actual': page_obj.number,
                'total_paginas': paginator.num_pages,
                'tiene_anterior': page_obj.has_previous(),
                'tiene_siguiente': page_obj.has_next(),
                'total_reportes': paginator.count
            },
            'filtros_aplicados': datos.get('filtros', {})
        }

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