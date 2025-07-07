#!/usr/bin/python
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

class IReporteColaborativoRepository:
    def __init__(self):
        pass

    def guardar(self, reporte):
        pass

    def buscar_por_id(self, reporte_id):
        pass

    @abstractmethod
    def obtener_todos(self, ):
        pass

    def buscar_por_zona(self, ubicacion, radio):
        pass

    def buscar_por_usuario(self, usuario_id):
        pass

    def buscar_por_tipo_incidente(self, tipo):
        pass

    def buscar_por_fecha_rango(self, fecha_inicio, fecha_fin):
        pass

    def buscar_reportes_validados(self, ):
        pass

    def actualizar(self, reporte):
        pass

    def eliminar(self, reporte_id):
        pass
