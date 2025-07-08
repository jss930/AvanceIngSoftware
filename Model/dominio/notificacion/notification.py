from datetime import datetime
from enum import Enum

class TipoNotificacion(Enum):
    GENERAL = "general"
    ALERTA_TRAFICO = "alerta_trafico"
    ALERTA_EMERGENCIA = "alerta_emergencia"
    ALERTA_UBICACION = "alerta_ubicacion"
    SISTEMA = "sistema"

class Notificacion:
    def __init__(self):
        self.notificacion_id = None
        self.usuario_id = None
        self.titulo = None
        self.mensaje = None
        self.tipo_notificacion = None
        self.fecha_envio = None
        self.fecha_lectura = None
        self.es_leida = False
        self.prioridad = 1
        self.datos_adicionales = {}

    def crear_notificacion(self, usuario_id, mensaje, tipo_notificacion="general", titulo=None):
        self.usuario_id = usuario_id
        self.mensaje = mensaje
        self.tipo_notificacion = tipo_notificacion
        self.titulo = titulo or "Notificación"
        self.fecha_envio = datetime.now()
        self.es_leida = False
        self.calcular_prioridad()

    def calcular_prioridad(self):
        """Calcular prioridad basada en tipo de notificación"""
        prioridades = {
            "alerta_emergencia": 5,
            "alerta_trafico": 4,
            "alerta_ubicacion": 3,
            "sistema": 2,
            "general": 1
        }
        self.prioridad = prioridades.get(self.tipo_notificacion, 1)

    def marcar_como_leida(self):
        self.es_leida = True
        self.fecha_lectura = datetime.now()

    def agregar_datos_adicionales(self, key, value):
        self.datos_adicionales[key] = value
