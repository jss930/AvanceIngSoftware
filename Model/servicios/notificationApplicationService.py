from datetime import datetime
from ..dominio.notificacion.notificacion import Notificacion, TipoNotificacion

class NotificationApplicationService:
    def __init__(self):
        self.notificacion_repository = None
        self.usuario_repository = None
        self.configuracion_repository = None

    def enviar_notificacion_usuario(self, usuario_id, mensaje, tipo="general", titulo=None):
        """Enviar notificación a un usuario específico"""
        try:
            # Verificar que el usuario existe
            usuario = self.usuario_repository.buscar_por_id(usuario_id)
            if not usuario:
                raise ValueError(f"Usuario {usuario_id} no encontrado")
            
            # Crear notificación
            notificacion = Notificacion()
            notificacion.crear_notificacion(
                usuario_id=usuario_id,
                mensaje=mensaje,
                tipo_notificacion=tipo,
                titulo=titulo or "Notificación"
            )
            
            # Guardar notificación
            self.notificacion_repository.guardar(notificacion)
            
            # Enviar notificación push/email si está configurado
            self._enviar_notificacion_externa(usuario, notificacion)
            
            return notificacion
            
        except Exception as e:
            raise Exception(f"Error al enviar notificación: {str(e)}")

    def obtener_notificaciones_no_leidas(self, usuario_id):
        """Obtener notificaciones no leídas de un usuario"""
        try:
            return self.notificacion_repository.obtener_por_usuario_no_leidas(usuario_id)
        except Exception as e:
            raise Exception(f"Error al obtener notificaciones: {str(e)}")

    def marcar_como_leida(self, notificacion_id, usuario_id):
        """Marcar una notificación como leída"""
        try:
            notificacion = self.notificacion_repository.buscar_por_id(notificacion_id)
            if not notificacion:
                raise ValueError("Notificación no encontrada")
            
            if notificacion.usuario_id != usuario_id:
                raise ValueError("No autorizado para modificar esta notificación")
            
            notificacion.marcar_como_leida()
            self.notificacion_repository.actualizar(notificacion)
            
            return notificacion
            
        except Exception as e:
            raise Exception(f"Error al marcar notificación como leída: {str(e)}")

    def obtener_estadisticas_notificaciones(self, usuario_id):
        """Obtener estadísticas de notificaciones del usuario"""
        try:
            total = self.notificacion_repository.contar_por_usuario(usuario_id)
            no_leidas = len(self.obtener_notificaciones_no_leidas(usuario_id))
            
            return {
                'total': total,
                'no_leidas': no_leidas,
                'leidas': total - no_leidas
            }
            
        except Exception as e:
            raise Exception(f"Error al obtener estadísticas: {str(e)}")

    def _enviar_notificacion_externa(self, usuario, notificacion):
        """Enviar notificación externa (push, email, SMS)"""
        try:
            # Verificar configuración del usuario
            config = self.configuracion_repository.buscar_por_usuario(usuario.usuario_id)
            if not config:
                return
            
            # Enviar notificación push si está habilitada
            if config.push_activo and usuario.token_push:
                self._enviar_push_notification(usuario.token_push, notificacion)
            
            # Enviar email si está habilitado
            if config.email_activo and usuario.email:
                self._enviar_email_notification(usuario.email, notificacion)
                
        except Exception as e:
            # Log error pero no fallar el proceso principal
            print(f"Error enviando notificación externa: {str(e)}")

    def _enviar_push_notification(self, token_push, notificacion):
        """Enviar notificación push"""
        # Implementar integración con servicio push (Firebase, etc.)
        pass

    def _enviar_email_notification(self, email, notificacion):
        """Enviar notificación por email"""
        # Implementar integración con servicio email
        pass