import requests

def reverse_geocode(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "json",
        "lat": lat,
        "lon": lon,
        "zoom": 20,
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "mi-aplicacion-ejemplo"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        address = data.get("address", {})

        calle = address.get("road") or address.get("pedestrian") or address.get("footway") or "Calle no encontrada"

        # Buscar posibles campos que contienen el distrito
        distrito_raw = (
            address.get("city_district") or
            address.get("suburb") or
            address.get("town") or
            address.get("village") or
            address.get("city") or
            "Distrito no encontrado"
        )

        # Si contiene " de ", probablemente es una urbanización: nos quedamos con lo último
        if " de " in distrito_raw.lower():
            distrito = distrito_raw.split(" de ")[-1]
        else:
            distrito = distrito_raw

        return {
            "calle": calle,
            "distrito": distrito.strip()
        }
    else:
        return {"error": f"Error en la solicitud: {response.status_code}"}

# Prueba
lat = -16.432199
lon = -71.503290
print("Probando...")
info = reverse_geocode(lat, lon)

if "error" in info:
    print(info["error"])
else:
    print(f"🚗 Calle o Avenida: {info['calle']}")
    print(f"🏘️ Distrito: {info['distrito']}")
