import folium
from folium.plugins import HeatMap
from typing import List, Dict


def generar_mapa_calor(reportes: List[Dict]) -> folium.Map:
    """
    Genera un mapa de calor basado en los reportes de tráfico.

    Args:
        reportes (List[Dict]): Lista de reportes con latitud, longitud y estado.

    Returns:
        folium.Map: Mapa generado con puntos de calor.
    """
    ubicaciones = [
        (r["latitud"], r["longitud"])
        for r in reportes
        if r.get("estado") == "congestionado"
    ]

    mapa = folium.Map(location=[-16.409, -71.537], zoom_start=13)
    HeatMap(ubicaciones).add_to(mapa)
    return mapa
