class NotificacionTraficoService:
    def __init__(self):
        self.usuario_repository = None
        self.reporte_repository = None
        self.notification_service = None
        self.radio_deteccion = 1000  # 1km por defecto

    def procesar_ubicacion_usuario(self, usuario_id, ubicacion_actual):
        """Procesar ubicación del usuario y detectar tráfico cercano"""
        
        # Verificar si el usuario tiene habilitadas las notificaciones de tráfico
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        if not self._usuario_tiene_notificaciones_activas(usuario):
            return
        
        # Buscar reportes activos en el área
        reportes_cercanos = self.reporte_repository.buscar_por_zona(
            ubicacion_actual, 
            self.radio_deteccion
        )
        
        # Filtrar reportes de tráfico/congestión
        reportes_trafico = [
            r for r in reportes_cercanos 
            if r.tipo_incidente in ['congestion', 'accident', 'road_closure']
        ]
        
        if reportes_trafico:
            self._enviar_notificacion_trafico(usuario_id, reportes_trafico, ubicacion_actual)

    def _usuario_tiene_notificaciones_activas(self, usuario):
        """Verificar si el usuario tiene activas las notificaciones de tráfico"""
        # Implementar lógica para verificar configuración del usuario
        # Por ahora, asumimos que todos los conductores las tienen activas
        from ..dominio.usuario.TipoUsuario import TipoUsuario
        return usuario.tipo_usuario == TipoUsuario.conductor

    def _enviar_notificacion_trafico(self, usuario_id, reportes, ubicacion_usuario):
        """Enviar notificación de tráfico al usuario"""
        
        # Determinar el reporte más cercano y crítico
        reporte_principal = self._seleccionar_reporte_principal(reportes, ubicacion_usuario)
        
        # Generar mensaje personalizado
        mensaje = self._generar_mensaje_trafico(reporte_principal, reportes)
        
        # Enviar notificación
        self.notification_service.enviar_notificacion_usuario(
            usuario_id=usuario_id,
            mensaje=mensaje,
            tipo="trafico_cercano"
        )

    def _seleccionar_reporte_principal(self, reportes, ubicacion_usuario):
        """Seleccionar el reporte más relevante"""
        # Por ahora, seleccionar el más cercano
        # En una implementación real, considerar también prioridad y tipo
        return reportes[0] if reportes else None

    def _generar_mensaje_trafico(self, reporte_principal, todos_reportes):
        """Generar mensaje personalizado para la notificación"""
        if not reporte_principal:
            return "Tráfico detectado en su área"
        
        tipo_incidente = {
            'congestion': 'Congestión',
            'accident': 'Accidente',
            'road_closure': 'Cierre de vía'
        }.get(reporte_principal.tipo_incidente, 'Incidente')
        
        mensaje = f"⚠️ {tipo_incidente} cercano: {reporte_principal.titulo}"
        
        if len(todos_reportes) > 1:
            mensaje += f" (y {len(todos_reportes)-1} más)"
        
        return mensaje

    def actualizar_configuracion_usuario(self, usuario_id, notificaciones_activas):
        """Permitir al usuario activar/desactivar notificaciones"""
        usuario = self.usuario_repository.buscar_por_id(usuario_id)
        # Actualizar configuración del usuario
        # Esto requeriría agregar el campo al modelo Usuario
        pass
s