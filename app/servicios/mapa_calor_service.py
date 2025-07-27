import folium
from folium.plugins import HeatMap
from app.reporte.models import ReporteColaborativo
import os

class MapaCalorService:
    def generar_mapa(self):
        # Centro de Arequipa como punto inicial
        m = folium.Map(location=[-16.4090474, -71.537451], zoom_start=13)

        # Lista para el heatmap
        heat_data = []

        # Colores según nivel de peligro
        colores = {
            1: 'green',
            2: 'orange',
            3: 'red',
            4: 'darkred'
        }

        # Obtener los reportes
        reportes = ReporteColaborativo.objects.filter(is_active=True)

        for r in reportes:
            if r.latitud and r.longitud:
                lat = float(r.latitud)
                lon = float(r.longitud)
                peso = r.nivel_peligro  # 1 a 4

                # Agregar al heatmap con peso
                heat_data.append([lat, lon, peso])

                # Agregar marcador con color según nivel
                color = colores.get(r.nivel_peligro, 'blue')
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=6 + peso,  # más grande si el nivel es más alto
                    color=color,
                    fill=True,
                    fill_opacity=0.8,
                    fill_color=color,
                    popup=f"{r.titulo} - {r.get_nivel_peligro_display()}"
                ).add_to(m)

        # Agregar capa heatmap
        if heat_data:
            HeatMap(heat_data, radius=20, blur=15, max_zoom=1).add_to(m)

        # Guardar el HTML
        ruta_html = os.path.join("app", "usuario", "templates", "mapa_generado.html")
        m.save(ruta_html)

        return ruta_html
