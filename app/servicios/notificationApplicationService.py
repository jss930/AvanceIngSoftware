#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.utils import timezone
from django.contrib.auth.models import User
from app.reporte.models import ReporteColaborativo
from app.usuario.models import PerfilUsuario
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class NotificationApplicationService:
    def __init__(self):
        self.notification_repository = None
        self.notification_factory = None
    
    def actualizar_ubicacion_usuario(self, usuario_id, latitud, longitud):
        """Actualiza la ubicación del usuario y verifica si necesita notificaciones"""
        try:
            user = User.objects.get(id=usuario_id)
            perfil = PerfilUsuario.get_or_create_for_user(user)
            
            # Actualizar ubicación
            perfil.latitud_actual = Decimal(str(latitud))
            perfil.longitud_actual = Decimal(str(longitud))
            perfil.ultima_actualizacion_ubicacion = timezone.now()
            perfil.save()
            
            # Verificar si hay zonas congestionadas cercanas
            if perfil.notificaciones_activas:
                return self.verificar_zonas_congestionadas_cercanas(user, latitud, longitud)
            
            return {'status': 'success', 'notifications': []}
            
        except User.DoesNotExist:
            return {'status': 'error', 'message': 'Usuario no encontrado'}
        except Exception as e:
            logger.error(f"Error actualizando ubicación: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def verificar_zonas_congestionadas_cercanas(self, user, latitud, longitud):
        """Verifica si hay zonas congestionadas cerca del usuario"""
        try:
            perfil = user.perfil
            radio = float(perfil.radio_notificacion)
            
            # Obtener reportes activos cercanos
            reportes_cercanos = ReporteColaborativo.get_incidents_near(
                latitude=latitud,
                longitude=longitud,
                radius_km=radio
            )
            
            # Filtrar por tipos de incidentes que el usuario quiere recibir
            tipos_notificar = perfil.tipos_incidentes_notificar
            if tipos_notificar:
                reportes_cercanos = [
                    r for r in reportes_cercanos 
                    if r.tipo_incidente in tipos_notificar
                ]
            
            # Filtrar solo reportes recientes (últimas 2 horas)
            reportes_recientes = [
                r for r in reportes_cercanos 
                if r.is_recent(hours=2)
            ]
            
            # Generar notificaciones
            notificaciones = []
            for reporte in reportes_recientes[:3]:  # Máximo 3 notificaciones
                distancia = reporte.get_distance_from(latitud, longitud)
                notificacion = {
                    'id': reporte.id,
                    'tipo': reporte.tipo_incidente,
                    'titulo': reporte.titulo,
                    'mensaje': self._generar_mensaje_notificacion(reporte, distancia),
                    'distancia': distancia,
                    'ubicacion': f"{reporte.nombre_via}, {reporte.distrito}",
                    'nivel_peligro': reporte.nivel_peligro,
                    'timestamp': timezone.now().isoformat()
                }
                notificaciones.append(notificacion)
            
            return {
                'status': 'success',
                'notifications': notificaciones,
                'total_reportes_cercanos': len(reportes_cercanos)
            }
            
        except Exception as e:
            logger.error(f"Error verificando zonas congestionadas: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _generar_mensaje_notificacion(self, reporte, distancia):
        """Genera el mensaje de notificación personalizado"""
        tipo_emoji = {
            'accidente': '🚗',
            'construccion': '🚧',
            'embotellamiento': '🚦',
            'cierre_via': '🚫',
            'control_policial': '👮',
            'semaforo_danado': '🔴',
            'bache': '🕳️',
            'inundacion': '💧',
            'vehiculo_averiado': '🔧',
            'manifestacion': '✊',
            'otro': '❓'
        }.get(reporte.tipo_incidente, '⚠️')
        
        nivel_texto = {
            1: 'Bajo',
            2: 'Medio', 
            3: 'Alto',
            4: 'Crítico'
        }.get(reporte.nivel_peligro, 'Medio')
        
        return (f"{tipo_emoji} {reporte.get_tipo_incidente_display()} detectado a {distancia}km. "
                f"Nivel: {nivel_texto}. Considera una ruta alternativa.")
    
    def obtener_configuracion_notificaciones(self, usuario_id):
        """Obtiene la configuración de notificaciones del usuario"""
        try:
            user = User.objects.get(id=usuario_id)
            perfil = PerfilUsuario.get_or_create_for_user(user)
            
            return {
                'status': 'success',
                'config': {
                    'notificaciones_activas': perfil.notificaciones_activas,
                    'radio_notificacion': float(perfil.radio_notificacion),
                    'frecuencia_actualizacion': perfil.frecuencia_actualizacion,
                    'tipos_incidentes_notificar': perfil.tipos_incidentes_notificar
                }
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def actualizar_configuracion_notificaciones(self, usuario_id, config):
        """Actualiza la configuración de notificaciones del usuario"""
        try:
            user = User.objects.get(id=usuario_id)
            perfil = PerfilUsuario.get_or_create_for_user(user)
            
            if 'notificaciones_activas' in config:
                perfil.notificaciones_activas = config['notificaciones_activas']
            
            if 'radio_notificacion' in config:
                perfil.radio_notificacion = config['radio_notificacion']
            
            if 'frecuencia_actualizacion' in config:
                perfil.frecuencia_actualizacion = config['frecuencia_actualizacion']
            
            if 'tipos_incidentes_notificar' in config:
                perfil.tipos_incidentes_notificar = config['tipos_incidentes_notificar']
            
            perfil.save()
            
            return {'status': 'success', 'message': 'Configuración actualizada'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def obtener_estadisticas_notificaciones(self, usuario_id):
        """Obtiene estadísticas de notificaciones para el usuario"""
        try:
            user = User.objects.get(id=usuario_id)
            perfil = user.perfil
            
            if not perfil.latitud_actual or not perfil.longitud_actual:
                return {
                    'status': 'success',
                    'stats': {
                        'reportes_cercanos': 0,
                        'zona_activa': False,
                        'ultima_actualizacion': None
                    }
                }
            
            # Obtener reportes cercanos actuales
            reportes_cercanos = ReporteColaborativo.get_incidents_near(
                latitude=float(perfil.latitud_actual),
                longitude=float(perfil.longitud_actual),
                radius_km=float(perfil.radio_notificacion)
            )
            
            reportes_recientes = [r for r in reportes_cercanos if r.is_recent(hours=2)]
            
            return {
                'status': 'success',
                'stats': {
                    'reportes_cercanos': len(reportes_recientes),
                    'zona_activa': len(reportes_recientes) > 0,
                    'ultima_actualizacion': perfil.ultima_actualizacion_ubicacion.isoformat() if perfil.ultima_actualizacion_ubicacion else None,
                    'radio_configurado': float(perfil.radio_notificacion)
                }
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}