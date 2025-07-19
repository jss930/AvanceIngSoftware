#!/usr/bin/python
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
# from .value_objects import Ubicacion


class ReporteColaborativo:
    def __init__(
        self,
        reporte_id: int,
        titulo: str,
        descripcion: str,
        usuario_reportador_id: int,
        ubicacion: Ubicacion,
        tipo_incidente: str,
        imagen_geolocalizada: Optional[str] = None
    ):
        self.reporte_id = reporte_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_creacion = datetime.now()
        self.fecha_actualizacion = datetime.now()
        self.usuario_reportador_id = usuario_reportador_id
        self.ubicacion = ubicacion
        self.estado_reporte = "pendiente"
        self.nivel_peligro = 1
        self.tipo_incidente = tipo_incidente
        self.imagen_geolocalizada = imagen_geolocalizada
        self.votos_positivos = 0
        self.votos_negativos = 0
        self.usuarios_votantes: List[int] = []
        self.es_validado = False

    def cambiar_estado(self, nuevo_estado: str, usuario_validador_id: int):
        self.estado_reporte = nuevo_estado
        self.fecha_actualizacion = datetime.now()

    def agregar_voto_validacion(self, usuario_id: int, voto: bool):
        if usuario_id in self.usuarios_votantes:
            return
        if voto:
            self.votos_positivos += 1
        else:
            self.votos_negativos += 1
        self.usuarios_votantes.append(usuario_id)

    def calcular_credibilidad(self) -> float:
        total = self.votos_positivos + self.votos_negativos
        return self.votos_positivos / total if total > 0 else 0.0

    def esta_en_zona(self, coordenadas: tuple[float, float], radio_km: float) -> bool:
        return self.ubicacion.esta_dentro(coordenadas, radio_km)

    def puede_ser_editado_por(self, usuario_id: int) -> bool:
        return self.usuario_reportador_id == usuario_id

    def es_reporte_reciente(self) -> bool:
        return (datetime.now() - self.fecha_creacion).days < 1

    def usuario_ya_voto(self, usuario_id: int) -> bool:
        return usuario_id in self.usuarios_votantes

    def calcular_nivel_peligro_automatico(self):
        desc = self.descripcion.lower()
        if "muerte" in desc or "choque" in desc:
            self.nivel_peligro = 3
        elif "herido" in desc or "congestion" in desc:
            self.nivel_peligro = 2
        else:
            self.nivel_peligro = 1
