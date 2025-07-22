import folium
from folium.plugins import HeatMap
import os
from web.models import ReporteColaborativo  # modelo de reportes
from django.conf import settings

class MapaCalorService:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def obtener_datos_reportes(self):
        datos = []
        reportes = ReporteColaborativo.objects.filter(es_validado=True)

        for reporte in reportes:
            try:
                lat_str, lon_str = reporte.ubicacion.split(",")
                lat, lon = float(lat_str.strip()), float(lon_str.strip())
                intensidad = reporte.nivel_peligro
                datos.append((lat, lon, intensidad))
            except Exception:
                continue

        return datos

    def generar_mapa(self):
        mapa = folium.Map(location=[-16.3988, -71.5369], zoom_start=13)
        heat_data = self.obtener_datos_reportes()
        HeatMap(heat_data).add_to(mapa)

        path_output = os.path.join(self.base_dir, "templates/mapa_embebido.html")
        mapa.save(path_output)
        return path_output
