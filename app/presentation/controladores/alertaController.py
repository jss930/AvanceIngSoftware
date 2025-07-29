from app.servicios.alertaApplicationService import AlertaApplicationService
from app.repositorio.alerta.alertaRepositoryImpl import AlertaRepositoryImpl


from app.admin_custom.models import HistorialNotificacion
from django.contrib.auth.models import User


alerta_service = AlertaApplicationService(AlertaRepositoryImpl())

def emitir_alerta(titulo, mensaje, enviado_por, destinatarios, ubicacion=None):
    alerta_service.crear_alerta(titulo, mensaje, enviado_por, destinatarios, ubicacion)

def obtener_alertas_usuario(usuario_id):
    return alerta_service.alertas_de_usuario(usuario_id)

def obtener_todas_alertas():
    return alerta_service.todas_las_alertas()



# --
alerta_service = AlertaApplicationService(AlertaRepositoryImpl())

def emitir_alerta(titulo, mensaje, enviado_por, destinatarios, ubicacion=None):
    # Crear la alerta
    alerta_service.crear_alerta(titulo, mensaje, enviado_por, destinatarios, ubicacion)
    
    # Obtener la alerta recién creada para registrar el historial
    from app.admin_custom.models import Alerta
    alerta_creada = Alerta.objects.filter(titulo=titulo, enviado_por=enviado_por).latest('fecha_envio')
    
    # Registrar en el historial según el tipo de envío
    if alerta_creada.enviar_a_todos:
        # Si es para todos, crear un registro general
        HistorialNotificacion.objects.create(
            alerta=alerta_creada,
            usuario_destinatario=None,  # None indica "todos"
            zona=ubicacion or "General",
            estado_entrega='enviado',
            tipo_notificacion='sistema'
        )
    else:
        # Si es para destinatarios específicos, crear un registro por cada uno
        for destinatario in destinatarios:
            HistorialNotificacion.objects.create(
                alerta=alerta_creada,
                usuario_destinatario=destinatario,
                zona=ubicacion or "General",
                estado_entrega='enviado',
                tipo_notificacion='sistema'
            )

def obtener_alertas_usuario(usuario_id):
    return alerta_service.alertas_de_usuario(usuario_id)

def obtener_todas_alertas():
    return alerta_service.todas_las_alertas()

# Nueva función para obtener el historial
def obtener_historial_notificaciones():
    return HistorialNotificacion.objects.select_related('alerta', 'usuario_destinatario').all()