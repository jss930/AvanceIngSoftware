from web.models import Alerta as AlertaModel
from django.contrib.auth.models import User
from app.dominio.alerta.iAlertaRepository import IAlertaRepository

class AlertaRepositoryImpl(IAlertaRepository):
    def guardar(self, alerta):
        alerta_db = AlertaModel.objects.create(
            titulo=alerta.titulo,
            mensaje=alerta.mensaje,
            ubicacion=alerta.ubicacion,
            enviado_por=alerta.enviado_por
        )
        alerta_db.destinatarios.set(alerta.destinatarios)
        alerta_db.save()

    def obtener_por_usuario(self, usuario_id):
        return AlertaModel.objects.filter(destinatarios__id=usuario_id).order_by('-fecha_envio')

    def listar_todas(self):
        return AlertaModel.objects.all().order_by('-fecha_envio')
