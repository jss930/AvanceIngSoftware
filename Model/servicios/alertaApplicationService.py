class AlertaApplicationService:
    def __init__(self):
        self.alerta_repository = None
        self.usuario_repository = None
        self.notification_service = None

    def crear_alerta_general(self, titulo, mensaje, tipo_alerta, usuario_creador_id):
        """Crear alerta para todos los usuarios"""
        from ..dominio.alerta.alerta import Alerta
        
        alerta = Alerta()
        alerta.crear_alerta(
            titulo=titulo,
            mensaje=mensaje,
            tipo_alerta=tipo_alerta,
            usuario_creador_id=usuario_creador_id,
            es_masiva=True
        )
        
        # Guardar alerta
        self.alerta_repository.guardar(alerta)
        
        # Obtener todos los usuarios activos
        usuarios_activos = self.usuario_repository.obtener_usuarios_activos()
        
        # Enviar notificación a todos los usuarios
        for usuario in usuarios_activos:
            self.notification_service.enviar_notificacion_usuario(
                usuario_id=usuario.usuario_id,
                mensaje=f"{titulo}: {mensaje}",
                tipo="alerta_general"
            )
        
        return alerta

    def crear_alerta_por_ubicacion(self, titulo, mensaje, tipo_alerta, 
                                 usuario_creador_id, ubicacion, radio_cobertura):
        """Crear alerta para usuarios en área específica"""
        from ..dominio.alerta.alerta import Alerta
        
        alerta = Alerta()
        alerta.crear_alerta(
            titulo=titulo,
            mensaje=mensaje,
            tipo_alerta=tipo_alerta,
            usuario_creador_id=usuario_creador_id,
            ubicacion=ubicacion,
            radio_cobertura=radio_cobertura
        )
        
        # Guardar alerta
        self.alerta_repository.guardar(alerta)
        
        # Obtener usuarios en el área
        usuarios_en_area = self._obtener_usuarios_en_area(ubicacion, radio_cobertura)
        
        # Enviar notificación a usuarios en el área
        for usuario in usuarios_en_area:
            self.notification_service.enviar_notificacion_usuario(
                usuario_id=usuario.usuario_id,
                mensaje=f"{titulo}: {mensaje}",
                tipo="alerta_ubicacion"
            )
        
        return alerta

    def _obtener_usuarios_en_area(self, ubicacion, radio):
        """Método auxiliar para obtener usuarios en área específica"""
        # Implementar lógica para obtener usuarios basado en su ubicación
        # Esto requeriría tener la ubicación actual de los usuarios
        pass

