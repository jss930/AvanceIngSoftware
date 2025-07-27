from app.servicios.alertaApplicationService import AlertaApplicationService
from app.repositorio.alerta.alertaRepositoryImpl import AlertaRepositoryImpl

alerta_service = AlertaApplicationService(AlertaRepositoryImpl())

def emitir_alerta(titulo, mensaje, enviado_por, destinatarios, ubicacion=None):
    alerta_service.crear_alerta(titulo, mensaje, enviado_por, destinatarios, ubicacion)

def obtener_alertas_usuario(usuario_id):
    return alerta_service.alertas_de_usuario(usuario_id)

def obtener_todas_alertas():
    return alerta_service.todas_las_alertas()