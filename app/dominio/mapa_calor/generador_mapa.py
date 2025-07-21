import folium
from folium.plugins import HeatMap
from typing import List, Dict

def generar_mapa_calor(reportes: List[Dict]) -> folium.Map:
    ubicaciones = [
        (r["latitud"], r["longitud"])
        for r in reportes
        if r.get("estado") == "congestionado"
    ]

    print("✅ Generando mapa con", len(ubicaciones), "puntos")

    mapa = folium.Map(location=[-16.409, -71.537], zoom_start=13)
    HeatMap(ubicaciones).add_to(mapa)
    return mapa
