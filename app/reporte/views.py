from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
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
        reporte = form.save(commit=False)
        reporte.save()
        print("Lat:", form.instance.latitud, "Lng:", form.instance.longitud)
        messages.success(self.request, "Reporte enviado exitosamente.")
        return super().form_valid(form)

    def get_address_from_coords(self, lat, lon):
        """Obtener dirección a partir de coordenadas usando ORS"""
        if hasattr(settings, 'ORS_API_KEY') and settings.ORS_API_KEY:
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
        return f"Lat: {lat}, Lng: {lon}"

    def get_coords_from_address(self, address):
        """Obtener coordenadas a partir de dirección usando ORS"""
        if hasattr(settings, 'ORS_API_KEY') and settings.ORS_API_KEY:
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
    def form_invalid(self, form):
        print("❌ Errores en el formulario:")
        print(form.errors.as_json())  
        messages.error(
            self.request, 
            'Hubo errores en el formulario. Por favor, corrígelos.'
        )
        return super().form_invalid(form)

# VISTA ADICIONAL PARA AJAX (opcional - para mejor experiencia de usuario)
@login_required
@require_http_methods(["POST"])
def report_incident_ajax(request):
    """Vista para manejar reportes via AJAX"""
    try:
        form = ReporteColaborativoForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.usuario_reportador = request.user
            reporte.save()

            return JsonResponse({
                'success': True,
                'message': 'Incidente reportado exitosamente',
                'incident_id': reporte.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Errores en el formulario'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        })


class SeeStateView(TemplateView):
    template_name = 'see_state.html'