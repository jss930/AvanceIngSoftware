#!/usr/bin/python
# -*- coding: utf-8 -*-

class INotificationRepository:
    def __init__(self):
        pass

    def guardar(self, notificacion):
        pass

    def buscar_por_usuario(self, usuario_id):
        pass

    def buscar_no_leidas(self, usuario_id):
        pass

    def buscar_por_tipo(self, tipo):
        pass

    def actualizar(self, notificacion):
        pass

    def eliminar(self, notificacion_id):
        pass

    def marcar_todas_leidas(self, usuario_id):
        pass
