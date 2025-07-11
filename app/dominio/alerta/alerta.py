class Alerta:
    def __init__(self, titulo, mensaje, enviado_por, destinatarios, ubicacion=None):
        self.titulo = titulo
        self.mensaje = mensaje
        self.ubicacion = ubicacion
        self.enviado_por = enviado_por
        self.destinatarios = destinatarios  # Lista de usuarios
