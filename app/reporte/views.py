from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import requests

from .models import ReporteColaborativo
from .forms import ReporteColaborativoForm

class ReporteIncidentView(LoginRequiredMixin, CreateView):
    model = ReporteColaborativo
    form_class = ReporteColaborativoForm
    template_name = 'report_incident.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        print("Entró al form_valid")

        lat = self.request.POST.get("latitud", "").strip()
        lng = self.request.POST.get("longitud", "").strip()
        ubicacion = self.request.POST.get("ubicacion", "").strip()

        if not (lat and lng) and not ubicacion:
            messages.error(self.request, "Debe proporcionar una ubicación o permitir acceso a su ubicación actual.")
            return self.form_invalid(form)

        # Si el usuario escribió una ubicación, geocodificamos con ORS
        if ubicacion and not (lat and lng):
            lat, lng = self.get_coords_from_address(ubicacion)
            if lat and lng:
                form.instance.latitud = lat
                form.instance.longitud = lng
                form.instance.ubicacion = ubicacion
            else:
                messages.error(self.request, "No se pudo geocodificar la dirección proporcionada.")
                return self.form_invalid(form)

        # Si el usuario proporcionó coordenadas, usamos ORS para generar la dirección
        elif lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                form.instance.latitud = lat
                form.instance.longitud = lng
                form.instance.ubicacion = self.get_address_from_coords(lat, lng)
            except ValueError:
                messages.error(self.request, "Coordenadas inválidas.")
                return self.form_invalid(form)

        # Asociamos el usuario autenticado
        form.instance.usuario_reportador = self.request.user
        obj = form.save(commit=False)
        obj.save()
        print("Lat:", form.instance.latitud, "Lng:", form.instance.longitud)
        messages.success(self.request, "Reporte enviado exitosamente.")
        return super().form_valid(form)

    def get_address_from_coords(self, lat, lon):
        url = "https://api.openrouteservice.org/geocode/reverse"
        headers = {'Authorization': settings.ORS_API_KEY}
        params = {
            'point.lat': lat,
            'point.lon': lon,
            'size': 1,
            'lang': 'es'
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["features"][0]["properties"]["label"]
        except Exception as e:
            print("Error ORS (reverse):", e)
            return None

    def get_coords_from_address(self, address):
        url = "https://api.openrouteservice.org/geocode/search"
        headers = {'Authorization': settings.ORS_API_KEY}
        params = {
            'text': address,
            'size': 1,
            'lang': 'es'
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            coords = data["features"][0]["geometry"]["coordinates"]  # [lon, lat]
            return coords[1], coords[0]
        except Exception as e:
            print("Error ORS (search):", e)
            return None, None