class IAlertaRepository:
    def __init__(self):
        pass

    def guardar(self, alerta):
        pass

    def buscar_por_id(self, alerta_id):
        pass

    def obtener_alertas_activas(self):
        pass

    def obtener_alertas_por_zona(self, ubicacion, radio):
        pass

    def obtener_alertas_por_usuario(self, usuario_id):
        pass

    def actualizar(self, alerta):
        pass

    def eliminar(self, alerta_id):
        pass
