class ConfiguracionUsuario:
    def __init__(self):
        self.usuario_id = None
        self.notificaciones_trafico_activas = True
        self.radio_notificaciones = 1000  # metros
        self.tipos_incidentes_interes = []
        self.horarios_notificacion = None  # Opcional: horarios específicos

    def actualizar_configuracion(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def debe_recibir_notificacion_trafico(self):
        return self.notificaciones_trafico_activas

    def esta_en_horario_notificacion(self):
        """Verificar si está en horario de notificaciones"""
        if not self.horarios_notificacion:
            return True
        
        # Implementar lógica de horarios
        return True