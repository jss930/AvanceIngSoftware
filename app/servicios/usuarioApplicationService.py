#!/usr/bin/python
# -*- coding: utf-8 -*-

class UsuarioApplicationService:
    def __init__(self):
        self.usuario_repository = None
        self.notification_service = None

    def crear_usuario(self, nombre, correo, clave, tipo_usuario):
        pass

    def autenticar_usuario(self, correo, clave):
        pass

    def obtener_usuario_por_id(self, usuario_id):
        pass

    def actualizar_perfil_usuario(self, usuario_id, datos_actualizacion):
        pass

    def cambiar_tipo_usuario(self, usuario_id, nuevo_tipo):
        pass

    def obtener_estadisticas_usuario(self, usuario_id):
        pass
