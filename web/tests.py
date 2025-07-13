from django.test import TestCase
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.dominio.mapa_calor.generador_mapa import generar_mapa_calor

def test_mapa_calor():
    """
    Prueba que el mapa de calor se genere correctamente con datos de prueba.
    """
    reportes = [
        {"latitud": -16.4091, "longitud": -71.5375, "estado": "congestionado"},
        {"latitud": -16.4100, "longitud": -71.5360, "estado": "fluido"},
        {"latitud": -16.4080, "longitud": -71.5380, "estado": "congestionado"}
    ]

    mapa = generar_mapa_calor(reportes)
    mapa.save("mapa_calor.html")
    print("✅ Mapa de calor generado exitosamente")

