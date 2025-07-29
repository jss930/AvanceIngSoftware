from django.conf import settings
from django.contrib import messages
from app.reporte.models import ReporteColaborativo
from app.reporte.forms import ReporteColaborativoForm
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test
from app.repositorio.alerta.alertaRepositoryImpl import AlertaRepositoryImpl
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from app.reporte.forms import ReporteColaborativoForm
from app.reporte.models import ReporteColaborativo
from web.services.reportes_usuario_service import (
    ReportesUsuarioService, 
    UsuarioSinReportesError, 
    UsuarioReporteError
)
from .forms import RegistroUsuarioForm, LoginForm
from app.presentation.controladores.reporteColaborativoController import ReporteColaborativoController
from io import StringIO
import json
import csv

# admin
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
@never_cache
def panel_personalizado(request):
    context = {
        'titulo': 'Panel Administrativo',
    }
    return render(request, 'panel/personalizado.html', context)

# Logout del admin
def logout_admin(request):
    logout(request)
    return redirect('custom_login')

# Registro existente (mantenida)
# from app.reporte.views import ReporteIncidentView
from app.servicios.mapa_calor_service import MapaCalorService
from django.utils.safestring import mark_safe

# Create your views here.
class RegistroUsuarioView(FormView):
    template_name = 'register.html'
    form_class = RegistroUsuarioForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"¡Bienvenido, {user.username}!")
        return super().form_valid(form)

# Nueva vista de login usando Class-Based View
class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'¡Bienvenido, {user.username}!')

            next_page = self.request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return super().form_valid(form)
        else:
            form.add_error(None, 'Usuario o contraseña incorrectos.')
            return self.form_invalid(form)


# Vista de logout (function-based es más simple para logout)
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obtener alertas
        alerta_repository = AlertaRepositoryImpl()
        alertas = alerta_repository.obtener_por_usuario(user.id)
        context['alertas'] = alertas
        context['user'] = user
        
        try:
            # Usar el servicio para obtener datos del dashboard
            service = ReportesUsuarioService(user.id)
            
            # Obtener reportes recientes para el dashboard
            recent_reports = service.obtener_reportes_recientes(limite=5)
            
            # Obtener estadísticas básicas
            if recent_reports:
                resultado = service.obtener_reportes_usuario()
                estadisticas = resultado['estadisticas']
            else:
                estadisticas = {
                    'total_reportes': 0,
                    'reportes_validados': 0,
                    'reportes_pendientes': 0,
                    'tasa_validacion': 0,
                    'promedio_credibilidad': 0
                }
            
            context['user_stats'] = {
                'total_reportes': estadisticas['total_reportes'],
                'validados': estadisticas['reportes_validados'],
                'pendientes': estadisticas['reportes_pendientes'],
                'credibilidad': round(estadisticas.get('promedio_credibilidad', 0))
            }
            
            context['recent_reports'] = recent_reports
            
        except (UsuarioSinReportesError, UsuarioReporteError) as e:
            # En caso de error o sin reportes, usar valores por defecto
            print(f"Error en DashboardView: {e}")  # Para debug
            context['user_stats'] = {
                'total_reportes': 0,
                'validados': 0,
                'pendientes': 0,
                'credibilidad': 0
            }
            context['recent_reports'] = []
        
        # Simular usuarios online
        context['users_online'] = "1,247"
        
        return context


class MisReportesView(LoginRequiredMixin, TemplateView):
    template_name = 'mis_reportes.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            service = ReportesUsuarioService(self.request.user.id)
            filtros = {
                'estado': self.request.GET.get('estado'),
                'tipo_incidente': self.request.GET.get('tipo_incidente'),
                'fecha_desde': self.request.GET.get('fecha_desde'),
                'nivel_peligro': self.request.GET.get('nivel_peligro'),  # Nuevo filtro
            }
            
            # Limpiar filtros vacíos
            filtros = {k: v for k, v in filtros.items() if v}
            
            pagina = self.request.GET.get('page', 1)
            resultado = service.obtener_reportes_usuario(filtros, pagina)
            
            context.update({
                'reportes': resultado['reportes'],
                'estadisticas': resultado['estadisticas'],
                'filtros_aplicados': resultado['filtros_aplicados'],
            })
            
        except UsuarioSinReportesError:
            context.update({
                'reportes': None,
                'estadisticas': None,
                'filtros_aplicados': {},
            })
        
        return context


class DetalleReporteView(LoginRequiredMixin, TemplateView):
    template_name = 'detalle_reporte.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reporte_id = self.kwargs.get('reporte_id')
        user = self.request.user
        
        try:
            # Obtener el reporte específico
            reporte = get_object_or_404(ReporteColaborativo, id=reporte_id)
            
            # Verificar permisos
            if reporte.usuario_reportador != user and not user.is_superuser:
                context['error'] = "No tienes permisos para ver este reporte"
            else:
                # Incrementar contador de vistas
                reporte.increment_views()
                
                # Calcular credibilidad
                total_votos = reporte.votos_positivos + reporte.votos_negativos
                if total_votos > 0:
                    credibilidad = round((reporte.votos_positivos * 100) / total_votos)
                else:
                    credibilidad = 0
                
                # Verificar si es reciente (usando el método del modelo)
                es_reciente = reporte.is_recent(hours=24)
                
                # Obtener ubicación usando los campos del modelo
                ubicacion_texto = ""
                if reporte.nombre_via and reporte.distrito:
                    ubicacion_texto = f"{reporte.nombre_via}, {reporte.distrito}"
                elif reporte.nombre_via:
                    ubicacion_texto = reporte.nombre_via
                elif reporte.distrito:
                    ubicacion_texto = reporte.distrito
                else:
                    ubicacion_texto = f"Lat: {reporte.latitud}, Lng: {reporte.longitud}"
                
                # Verificar si puede editar
                puede_editar = (reporte.estado_reporte == 'pendiente' and 
                              reporte.can_be_edited_by(user))
                
                context.update({
                    'reporte': reporte,
                    'credibilidad': credibilidad,
                    'angulo_grafico': credibilidad * 3.6,
                    'es_reciente': es_reciente,
                    'ubicacion_texto': ubicacion_texto,
                    'puede_editar': puede_editar,
                })
                
        except Exception as e:
            context['error'] = f"Error al cargar el reporte: {str(e)}"
            
        return context


@login_required
def vista_configuracion_usuario(request):
    """Vista para configuración de usuario (función basada)"""
    from web.services.reportes_usuario_service import ConfiguracionUsuarioService, ConfiguracionInvalidaError
    
    config_service = ConfiguracionUsuarioService(request.user.id)
    
    if request.method == 'POST':
        try:
            nuevos_datos = {
                'reportes_por_pagina': int(request.POST.get('reportes_por_pagina', 10)),
                'mostrar_estadisticas': request.POST.get('mostrar_estadisticas') == 'on',
                'notificaciones_activas': request.POST.get('notificaciones_activas') == 'on'
            }
            
            configuracion = config_service.actualizar_configuracion(nuevos_datos)
            
            context = {
                'configuracion': configuracion,
                'mensaje_exito': 'Configuración actualizada correctamente'
            }
            
        except ConfiguracionInvalidaError as e:
            context = {
                'configuracion': config_service.obtener_configuracion(),
                'error': str(e)
            }
    else:
        context = {
            'configuracion': config_service.obtener_configuracion()
        }
    
    return render(request, 'configuracion_usuario.html', context)


# Tus vistas existentes (mantenidas)
def home(request):
    return render(request, 'home.html')

def register(request):
    return render(request, 'register.html')

def test(request):
    return render(request, 'test.html')

# Vista funcional para generar el mapa de calor y mostrar la página
def vista_mapa_calor(request):
    servicio = MapaCalorService()
    ruta_html = servicio.generar_mapa()

    with open(ruta_html, "r", encoding="utf-8") as f:
        mapa_html = f.read()

    return render(request, "mapa_calor_page.html", {"mapa_html": mapa_html})



def mapa_embebido_view(request):
    return render(request, "mapa_embebido.html")

# Vistas para botones del home
class PlanRouteView(TemplateView):
    template_name = 'plan_route.html'


class ReporteIncidentView(CreateView):
    model = ReporteColaborativo
    form_class = ReporteColaborativoForm
    template_name = 'report_incident.html'
    success_url = reverse_lazy('dashboard') 

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.usuario_reportador = self.request.user
        else:
            form.add_error(None, "Debes iniciar sesión para enviar un reporte.")
            return self.form_invalid(form)
        return super().form_valid(form)


class EditarReporteView(LoginRequiredMixin, UpdateView):
    model = ReporteColaborativo
    form_class = ReporteColaborativoForm
    template_name = 'editar_reporte.html'
    success_url = reverse_lazy('mis_reportes')
    login_url = 'login'

    def get_queryset(self):
        # Solo permite editar reportes del usuario actual
        return ReporteColaborativo.objects.filter(usuario_reportador=self.request.user)

    def form_invalid(self, form):
        form.add_error(None, "Revisa los datos del formulario.")
        return super().form_invalid(form)


class EliminarReporteView(LoginRequiredMixin, DeleteView):
    model = ReporteColaborativo
    template_name = 'eliminar_reporte.html'
    success_url = reverse_lazy('mis_reportes')
    login_url = 'login'

    def get_queryset(self):
        return ReporteColaborativo.objects.filter(usuario_reportador=self.request.user)



class SeeStateView(TemplateView):
    template_name = 'see_state.html'