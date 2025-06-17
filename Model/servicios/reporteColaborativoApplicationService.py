#!/usr/bin/python
# -*- coding: utf-8 -*-

class ReporteColaborativoApplicationService:
    def __init__(self):
        self.reporte_repository = None
        self.usuario_repository = None
        self.reporte_factory = None
        self.servicio_validacion = None
        self.mapa_calor_service = None

    def registrar_nuevo_reporte(self, descripcion, usuario_id, ubicacion, imagen_url, tipo_incidente):
        pass

    def procesar_validacion_reporte(self, reporte_id):
        pass

    def cambiar_estado_reporte(self, reporte_id, nuevo_estado, usuario_validador_id):
        pass

    def obtener_reportes_por_zona(self, coordenadas, radio):
        pass

    def votar_validacion_reporte(self, reporte_id, usuario_id, voto):
        pass

    def generar_estadisticas_reportes(self, fecha_inicio, fecha_fin):
        pass

    def obtener_reportes_usuario(self, usuario_id):
        pass
