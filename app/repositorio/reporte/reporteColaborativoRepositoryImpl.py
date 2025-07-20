#!/usr/bin/python
# -*- coding: utf-8 -*-

from app.dominio.reporte.interface1 import Interface1
from app.reporte.models import ReporteColaborativo
from app.dominio.reporte.iReporteColaborativoRepository import IReporteColaborativoRepository



class ReporteColaborativoRepositoryImpl(IReporteColaborativoRepository):
    def obtener_todos(self):
        return ReporteColaborativo.objects.all()