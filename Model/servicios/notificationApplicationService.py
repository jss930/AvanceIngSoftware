#!/usr/bin/python
# -*- coding: utf-8 -*-

class NotificationApplicationService:
    def __init__(self):
        self.notification_repository = None
        self.notification_factory = None

    def enviar_notificacion_usuario(self, usuario_id, mensaje, tipo):
        pass

    def enviar_notificacion_masiva(self, usuarios_ids, mensaje, tipo):
        pass

    def obtener_notificaciones_no_leidas(self, usuario_id):
        pass

    def procesar_notificacion_reporte(self, reporte_id):
        pass

    def notificar_reporte_cercano(self, usuario_id, reporte):
        pass
