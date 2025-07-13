#!/usr/bin/python
# -*- coding: utf-8 -*-

class Notification:
    def __init__(self):
        self.notificacion_id = None
        self.usuario_destinatario_id = None
        self.titulo = None
        self.mensaje = None
        self.fecha_envio = None
        self.fecha_lectura = None
        self.tipo_notificacion = None
        self.es_leida = None
        self.prioridad = None
        self.datos_adicionales = None
        self.referencia_reporte_id = None

    def marcar_como_leida(self, ):
        pass

    def es_notificacion_urgente(self, ):
        pass

    def tiempo_desde_envio(self, ):
        pass

    def generar_contenido_personalizado(self, usuario):
        pass

    def calcular_prioridad(self, ):
        pass
