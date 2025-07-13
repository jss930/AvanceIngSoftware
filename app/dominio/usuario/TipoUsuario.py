#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum

class TipoUsuario(Enum):
    administrador = 1
    conductor = 2
    ciclista = 3
    colaborador = 4
    peaton = 5
    anonimo = 6
