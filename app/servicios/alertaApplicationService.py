from app.dominio.alerta.alerta import Alerta

class AlertaApplicationService:
    def __init__(self, alerta_repo):
        self.alerta_repo = alerta_repo

    def crear_alerta(self, titulo, mensaje, enviado_por, destinatarios, ubicacion=None):
        alerta = Alerta(titulo, mensaje, enviado_por, destinatarios, ubicacion)
        self.alerta_repo.guardar(alerta)

    def alertas_de_usuario(self, usuario_id):
        return self.alerta_repo.obtener_por_usuario(usuario_id)

    def todas_las_alertas(self):
        return self.alerta_repo.listar_todas()
