#!/usr/bin/python
# -*- coding: utf-8 -*-
from app.servicios.reporteColaborativoApplicationService import ReporteColaborativoApplicationService

class ReporteColaborativoController:
    def __init__(self):
        self.reporte_app_service = ReporteColaborativoApplicationService()

    def crear_reporte(self, datos_reporte):
        pass

    def obtener_reporte(self, reporte_id):
        pass

    def obtener_todos(self):
        return self.reporte_app_service.listar_repotes()

    def listar_reportes(self, filtros):
        pass

    def actualizar_estado_reporte(self, reporte_id, nuevo_estado):
        pass

    def eliminar_reporte(self, reporte_id):
        pass
