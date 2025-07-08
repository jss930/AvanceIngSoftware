from datetime import datetime
from enum import Enum

class TipoAlerta(Enum):
    EMERGENCIA = "emergencia"
    TRAFICO = "trafico"
    INFORMATIVA = "informativa"
    ZONA_PELIGROSA = "zona_peligrosa"

class Alerta:
    def __init__(self):
        self.alerta_id = None
        self.titulo = None
        self.mensaje = None
        self.tipo_alerta = None
        self.ubicacion = None  # Opcional - coordenadas lat, lng
        self.radio_cobertura = None  # En metros
        self.fecha_creacion = None
        self.fecha_expiracion = None
        self.es_activa = None
        self.prioridad = None
        self.usuario_creador_id = None
        self.usuarios_objetivo = []  # Lista de IDs de usuarios específicos
        self.es_masiva = False  # Si es para todos los usuarios

    def crear_alerta(self, titulo, mensaje, tipo_alerta, usuario_creador_id, 
                     ubicacion=None, radio_cobertura=None, es_masiva=False):
        self.titulo = titulo
        self.mensaje = mensaje
        self.tipo_alerta = tipo_alerta
        self.usuario_creador_id = usuario_creador_id
        self.ubicacion = ubicacion
        self.radio_cobertura = radio_cobertura
        self.es_masiva = es_masiva
        self.fecha_creacion = datetime.now()
        self.es_activa = True
        self.calcular_prioridad()

    def calcular_prioridad(self):
        """Calcular prioridad basada en tipo de alerta"""
        prioridades = {
            TipoAlerta.EMERGENCIA: 5,
            TipoAlerta.ZONA_PELIGROSA: 4,
            TipoAlerta.TRAFICO: 3,
            TipoAlerta.INFORMATIVA: 1
        }
        self.prioridad = prioridades.get(self.tipo_alerta, 1)

    def es_usuario_en_area(self, usuario_ubicacion):
        """Verificar si un usuario está en el área de cobertura"""
        if not self.ubicacion or not usuario_ubicacion:
            return False
        
        # Calcular distancia entre ubicaciones (implementación simplificada)
        import math
        
        lat1, lng1 = self.ubicacion
        lat2, lng2 = usuario_ubicacion
        
        # Fórmula de Haversine para calcular distancia
        R = 6371000  # Radio de la Tierra en metros
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        distancia = R * c
        return distancia <= self.radio_cobertura

    def desactivar_alerta(self):
        self.es_activa = False