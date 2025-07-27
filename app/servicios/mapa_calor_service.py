from pathlib import Path
import folium
from app.reporte.models import ReporteColaborativo

class MapaCalorService:
    def generar_mapa(self):
        # Crear un mapa base
        mapa = folium.Map(location=[-16.409, -71.537], zoom_start=13)

        # Tomamos los reportes de la BD
        reportes = ReporteColaborativo.objects.all()

        # Añadir marcadores simples
        for r in reportes:
            try:
                lat = float(r.latitud)
                lon = float(r.longitud)

                # Añadimos marcador al mapa
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=6,
                    popup=f"{r.titulo} - {r.tipo_incidente}",
                    color="red",
                    fill=True,
                    fill_color="red",
                ).add_to(mapa)
            except Exception as e:
                print(f"Error al agregar reporte {r.id}: {e}")

        # Ruta de salida
        output_dir = Path("app/usuario/templates")
        output_dir.mkdir(parents=True, exist_ok=True)
        ruta_html = output_dir / "mapa_embebido.html"

        # Guardamos el HTML
        mapa.save(str(ruta_html))

        # RETORNAMOS la ruta
        return ruta_html
