#!/usr/bin/python
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

class IReporteColaborativoRepository:
    #def __init__(self):
    #    pass

    @abstractmethod
    def guardar(self, reporte):
        """
        Guarda un nuevo reporte colaborativo.
        """
        pass

    @abstractmethod
    def buscar_por_id(self, reporte_id):
        """
        Busca un reporte por su ID único.
        """
        pass

    @abstractmethod
    def obtener_todos(self, ):
        """
        Retorna todos los reportes almacenados.
        """
        pass

    @abstractmethod
    def buscar_por_zona(self, ubicacion, radio):
        """
        Busca reportes dentro de un radio geográfico desde una ubicación específica.
        """
        pass

    @abstractmethod
    def buscar_por_usuario(self, usuario_id):
        """
        Retorna los reportes hechos por un usuario específico.
        """
        pass

    @abstractmethod
    def buscar_por_tipo_incidente(self, tipo):
        """
        Retorna los reportes que coinciden con un tipo de incidente.
        """
        pass

    @abstractmethod
    def buscar_por_fecha_rango(self, fecha_inicio, fecha_fin):
        """
        Retorna los reportes que fueron creados entre dos fechas.
        """
        pass

    @abstractmethod
    def buscar_reportes_validados(self, ):
        """
        Retorna los reportes que han sido validados por un administrador.
        """
        pass

    @abstractmethod
    def actualizar(self, reporte):
        """
        Actualiza la información de un reporte existente.
        """
        pass

    @abstractmethod
    def eliminar(self, reporte_id):
        """
        Elimina un reporte basado en su ID.
        """
        pass
