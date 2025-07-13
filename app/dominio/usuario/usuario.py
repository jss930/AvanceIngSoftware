#!/usr/bin/python
# -*- coding: utf-8 -*-

class usuario:
    def __init__(self):
        self.usuario_id = None
        self.nombre = None
        self.correo = None
        self.clave_hash = None
        self.fecha_registro = None
        self.tipo_usuario = None
        self.estado_activo = None
        self.puntuacion_credibilidad = None
        self.total_reportes_creados = None
        self.total_votos_dados = None

    def verificar_clave(self, clave_ingresada):
        pass

    def actualizar_perfil(self, nuevos_datos):
        pass

    def cambiar_clave(self, clave_nueva):
        pass

    def es_administrador(self, ):
        pass

    def es_moderador(self, ):
        pass

    def activar_cuenta(self, ):
        pass

    def desactivar_cuenta(self, ):
        pass

    def incrementar_credibilidad(self, puntos):
        pass

    def puede_votar_reporte(self, ):
        pass
