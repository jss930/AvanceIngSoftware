# ==> /home/gerardo/Descargas/AvanceIngSoftware/traffic/views_alertas.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from decimal import Decimal

@csrf_exempt
@require_http_methods(["POST"])
def crear_alerta(request):
    """
    API para crear alertas - Tarea 1
    POST /api/alertas/crear/
    """
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        required_fields = ['titulo', 'mensaje', 'tipo_alerta']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'error': f'Campo requerido: {field}',
                    'success': False
                }, status=400)
        
        # Crear alerta
        alerta_data = {
            'titulo': data['titulo'],
            'mensaje': data['mensaje'],
            'tipo_alerta': data['tipo_alerta'],
            'usuario_creador_id': data.get('usuario_creador_id', 1),  # Por defecto admin
            'ubicacion': data.get('ubicacion'),
            'radio_cobertura': data.get('radio_cobertura'),
            'es_masiva': data.get('es_masiva', False)
        }
        
        # Instanciar servicio (en implementación real sería inyectado)
        from ..Model.servicios.alertaApplicationService import AlertaApplicationService
        alerta_service = AlertaApplicationService()
        
        # Crear alerta según tipo
        if alerta_data['ubicacion'] and alerta_data['radio_cobertura']:
            alerta = alerta_service.crear_alerta_por_ubicacion(
                titulo=alerta_data['titulo'],
                mensaje=alerta_data['mensaje'],
                tipo_alerta=alerta_data['tipo_alerta'],
                usuario_creador_id=alerta_data['usuario_creador_id'],
                ubicacion=alerta_data['ubicacion'],
                radio_cobertura=alerta_data['radio_cobertura']
            )
        else:
            alerta = alerta_service.crear_alerta_general(
                titulo=alerta_data['titulo'],
                mensaje=alerta_data['mensaje'],
                tipo_alerta=alerta_data['tipo_alerta'],
                usuario_creador_id=alerta_data['usuario_creador_id']
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Alerta creada exitosamente',
            'alerta_id': alerta.alerta_id
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON inválido',
            'success': False
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'success': False
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def procesar_ubicacion_usuario(request):
    """
    API para procesar ubicación del usuario - Tarea 2
    POST /api/usuarios/ubicacion/
    """
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        required_fields = ['usuario_id', 'latitud', 'longitud']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'error': f'Campo requerido: {field}',
                    'success': False
                }, status=400)
        
        usuario_id = data['usuario_id']
        ubicacion_actual = (
            float(data['latitud']),
            float(data['longitud'])
        )
        
        # Procesar ubicación
        from ..Model.servicios.notificacionTraficoService import NotificacionTraficoService
        trafico_service = NotificacionTraficoService()
        
        trafico_service.procesar_ubicacion_usuario(usuario_id, ubicacion_actual)
        
        return JsonResponse({
            'success': True,
            'message': 'Ubicación procesada correctamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON inválido',
            'success': False
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'success': False
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def configurar_notificaciones_usuario(request):
    """
    API para configurar notificaciones del usuario - Tarea 2
    POST /api/usuarios/configurar-notificaciones/
    """
    try:
        data = json.loads(request.body)
        
        usuario_id = data.get('usuario_id')
        if not usuario_id:
            return JsonResponse({
                'error': 'usuario_id requerido',
                'success': False
            }, status=400)
        
        # Configuraciones disponibles
        configuraciones = {
            'notificaciones_trafico_activas': data.get('notificaciones_trafico_activas', True),
            'radio_notificaciones': data.get('radio_notificaciones', 1000),
            'tipos_incidentes_interes': data.get('tipos_incidentes_interes', [])
        }
        
        # Actualizar configuración
        from ..Model.servicios.notificacionTraficoService import NotificacionTraficoService
        trafico_service = NotificacionTraficoService()
        
        trafico_service.actualizar_configuracion_usuario(
            usuario_id=usuario_id,
            notificaciones_activas=configuraciones['notificaciones_trafico_activas']
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Configuración actualizada correctamente',
            'configuraciones': configuraciones
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'JSON inválido',
            'success': False
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'success': False
        }, status=500)

@require_http_methods(["GET"])
def obtener_notificaciones_usuario(request, usuario_id):
    """
    API para obtener notificaciones del usuario
    GET /api/usuarios/{usuario_id}/notificaciones/
    """
    try:
        from ..Model.servicios.notificationApplicationService import NotificationApplicationService
        notification_service = NotificationApplicationService()
        
        # Obtener notificaciones no leídas
        notificaciones = notification_service.obtener_notificaciones_no_leidas(usuario_id)
        
        # Serializar notificaciones (implementación simplificada)
        notificaciones_data = []
        for notif in notificaciones:
            notificaciones_data.append({
                'id': notif.notificacion_id,
                'titulo': notif.titulo,
                'mensaje': notif.mensaje,
                'tipo': notif.tipo_notificacion,
                'fecha_envio': notif.fecha_envio.isoformat() if notif.fecha_envio else None,
                'es_leida': notif.es_leida,
                'prioridad': notif.prioridad
            })
        
        return JsonResponse({
            'success': True,
            'notificaciones': notificaciones_data,
            'total': len(notificaciones_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error interno: {str(e)}',
            'success': False
        }, status=500)