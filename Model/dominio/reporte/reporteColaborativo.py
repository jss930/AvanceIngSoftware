#!/usr/bin/python
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class ReporteColaborativo:
    def __init__(self):
        self.reporte_id = None
        self.titulo = None
        self.descripcion = None
        self.fecha_creacion = None
        self.fecha_actualizacion = None
        self.usuario_reportador_id = None
        self.ubicacion = None
        self.estado_reporte = None
        self.nivel_peligro = None
        self.tipo_incidente = None
        self.imagen_geolocalizada = None
        self.votos_positivos = None
        self.votos_negativos = None
        self.usuarios_votantes = None
        self.es_validado = None
    
    @abstractmethod
    def cambiar_estado(self, nuevo_estado, usuario_validador_id):
        pass

    @abstractmethod
    def agregar_voto_validacion(self, usuario_id, voto):
        pass

    @abstractmethod
    def calcular_credibilidad(self, ):
        pass

    @abstractmethod
    def esta_en_zona(self, coordenadas, radio):
        pass

    @abstractmethod
    def puede_ser_editado_por(self, usuario_id):
        pass

    @abstractmethod
    def es_reporte_reciente(self, ):
        pass

    @abstractmethod
    def obtener_coordenadas(self, ):
        pass

    @abstractmethod
    def usuario_ya_voto(self, usuario_id):
        pass

    @abstractmethod
    def validar_datos_internos(self, ):
        pass

    @abstractmethod
    def calcular_nivel_peligro_automatico(self, ):
        pass
