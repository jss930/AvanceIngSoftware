
# Proyecto de Visualización de Mapa de Calor de Tráfico

Este módulo del sistema implementa la visualización de un mapa de calor con datos de tráfico urbano utilizando Python, Django y Folium.

##  Objetivo
Mostrar visualmente los puntos congestionados de una ciudad en un mapa interactivo, como parte de la historia de usuario:

**H1**: _Como usuario, quiero ver un mapa con colores que indiquen el nivel de tráfico, para decidir la mejor ruta._

---

## 🚀 Funcionalidad Implementada

- Vista `ver-mapa/` creada en Django (`views.py`)
- Uso de la función `generar_mapa_calor()` con Folium
- Mapa exportado a archivo `mapa_calor.html` dentro de `web/static`
- Visualización embebida usando `<iframe>` en la plantilla `see_state.html`
- Rutas organizadas en `web/urls.py`
- Commit realizado con separación modular
- Análisis con SonarLint sin errores críticos

---

## Estilos de Programación Aplicados

### 1. Cookbook

Una función con entrada clara (`reportes`), procesamiento y retorno (`folium.Map`):

```python
def generar_mapa_calor(reportes: List[Dict]) -> folium.Map:
    ubicaciones = [(r["latitud"], r["longitud"]) for r in reportes if r.get("estado") == "congestionado"]
    mapa = folium.Map(location=[-16.409, -71.537], zoom_start=13)
    HeatMap(ubicaciones).add_to(mapa)
    return mapa
```

---

### 2.  Pipeline

Flujo lineal: datos → generación de mapa → guardado → respuesta web:

```python
mapa = generar_mapa_calor(reportes)
mapa.save(ruta_mapa)
return render(request, "see_state.html", {"mapa_html": mapa_html})
```

---

### 3. Error/Exception Handling

Manejo de errores al leer archivos HTML generados:

```python
try:
    with open(ruta_mapa, "r", encoding="utf-8") as f:
        mapa_html = f.read()
except Exception as e:
    mapa_html = "<p>Error al cargar el mapa</p>"
```

---

### 4. Trinity

Separación en capas:
- Datos simulados o del sistema
- Lógica de mapa en módulo independiente
- Presentación en plantilla `see_state.html`

---

## Estructura Relevante

```
web/
├── views.py            # Vista ver-mapa
├── urls.py             # Ruta ver-mapa/
├── static/
│   └── mapa_calor.html # Archivo HTML del mapa
├── templates/
│   └── see_state.html  # Plantilla con iframe
└── ...
```

---

## 🧪 Requisitos Técnicos

- Python 3.12
- Django 5.x
- Folium
- SonarLint (instalado como extensión en PyCharm)

---
