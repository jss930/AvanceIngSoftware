from app.reporte.models import ReporteColaborativo
import folium
from folium.plugins import HeatMap
from django.conf import settings
import os

class MapaCalorService:
    def generar_mapa(self):
        # Datos de los reportes
        heat_data = []
        for r in ReporteColaborativo.objects.all():
            try:
                heat_data.append([float(r.latitud), float(r.longitud)])
            except Exception:
                pass  # Ignorar si hay coordenadas inválidas

        # Crear mapa centrado
        m = folium.Map(location=[-16.3989, -71.535], zoom_start=13)
        if heat_data:
            HeatMap(heat_data).add_to(m)

        # Guardar mapa en HTML
        ruta_html = os.path.join(settings.BASE_DIR, "app/usuario/templates/mapa_generado.html")
        m.save(ruta_html)
        return ruta_html
