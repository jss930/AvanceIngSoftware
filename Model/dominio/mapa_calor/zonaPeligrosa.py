#!/usr/bin/python
# -*- coding: utf-8 -*-

class ZonaPeligrosa:
    def __init__(self):
        self.zona_id = None
        self.nombre_zona = None
        self.ubicacion_centro = None
        self.radio_cobertura = None
        self.nivel_peligro_actual = None
        self.fecha_actualizacion = None
        self.cantidad_reportes = None
        self.reportes_asociados = None
        self.tendencia = None

    def actualizar_nivel_peligro(self, ):
        pass

    def agregar_reporte(self, reporte_id):
        pass

    def calcular_nivel_peligro_por_reportes(self, ):
        pass

    def obtener_estadisticas_zona(self, ):
        pass

    def es_zona_caliente(self, ):
        pass

    def obtener_reportes_recientes(self, dias):
        pass

    def recalcular_tendencia(self, ):
        pass
