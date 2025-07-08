class INotificacionRepository:
    def __init__(self):
        pass

    def guardar(self, notificacion):
        """Guardar una notificación"""
        pass

    def buscar_por_id(self, notificacion_id):
        """Buscar notificación por ID"""
        pass

    def obtener_por_usuario_no_leidas(self, usuario_id):
        """Obtener notificaciones no leídas de un usuario"""
        pass

    def obtener_por_usuario(self, usuario_id, limite=None):
        """Obtener todas las notificaciones de un usuario"""
        pass

    def actualizar(self, notificacion):
        """Actualizar una notificación"""
        pass

    def eliminar(self, notificacion_id):
        """Eliminar una notificación"""
        pass

    def contar_por_usuario(self, usuario_id):
        """Contar notificaciones de un usuario"""
        pass

    def marcar_todas_como_leidas(self, usuario_id):
        """Marcar todas las notificaciones de un usuario como leídas"""
        pass