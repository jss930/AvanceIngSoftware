#!/usr/bin/python
# -*- coding: utf-8 -*-
from app.repositorio.reporte.reporteColaborativoRepositoryImpl import ReporteColaborativoRepositoryImpl

class ReporteColaborativoApplicationService:
    def __init__(self):
        self.reporte_repository = ReporteColaborativoRepositoryImpl()
        self.usuario_repository = None
        self.reporte_factory = None
        self.servicio_validacion = None
        self.mapa_calor_service = None

    def registrar_nuevo_reporte(self, descripcion, usuario_id, ubicacion, imagen_url, tipo_incidente):
        # Metodo pendiente de implementación (Registro de nuevo reporte)
        pass

    def procesar_validacion_reporte(self, reporte_id):
        # Metodo pendiente de implementación (Validación del reporte)
        pass

    def cambiar_estado_reporte(self, reporte_id, nuevo_estado, usuario_validador_id):
        # Metodo pendiente de implementación (Cambio de estado)
        pass

    def obtener_reportes_por_zona(self, coordenadas, radio):
        # Metodo pendiente de implementación (Filtrado por zona)
        pass

    def votar_validacion_reporte(self, reporte_id, usuario_id, voto):
        # Metodo pendiente de implementación (Voto de validación)
        pass

    def generar_estadisticas_reportes(self, fecha_inicio, fecha_fin):
        # Metodo pendiente de implementación (Estadísticas por fecha)
        pass

    def obtener_reportes_usuario(self, usuario_id):
        # Metodo pendiente de implementación (Reportes por usuario)
        pass

    def listar_repotes(self):
        return self.reporte_repository.obtener_todos()

    def obtener_reporte_por_id(self, reporte_id):
        return self.reporte_repository.buscar_por_id(reporte_id)

    def actualizar_reporte_completo(self, reporte_id, nuevo_reporte):
        existente = self.reporte_repository.buscar_por_id(reporte_id)
        if existente:
            existente.titulo = nuevo_reporte.titulo
            existente.descripcion = nuevo_reporte.descripcion
            existente.ubicacion = nuevo_reporte.ubicacion
            existente.tipo_incidente = nuevo_reporte.tipo_incidente
            existente.estado_reporte = nuevo_reporte.estado_reporte
            self.reporte_repository.actualizar(existente)
