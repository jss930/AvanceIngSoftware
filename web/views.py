from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
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
from django.views.generic.edit import CreateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from web.models import Reporte
from web.services.reportes_usuario_service import (
    ReportesUsuarioService, 
    UsuarioSinReportesError, 
    UsuarioReporteError
)
from .forms import RegistroUsuarioForm, LoginForm, ReporteColaborativoForm
from app.presentation.controladores.reporteColaborativoController import ReporteColaborativoController
from .models import ReporteColaborativo
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
        # Redirige si ya está autenticado
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
            
            # Redirige a la página solicitada o al dashboard
            next_page = self.request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return super().form_valid(form)
        else:
            form.add_error(None, 'Usuario o contraseña incorrectos.')
            return self.form_invalid(form)


# Vista de logout (function-based es más simple para logout)
def logout_view(request):
    """Vista para logout de usuarios"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
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
                    'tasa_validacion': 0
                }
            
            context['user_stats'] = {
                'total_reportes': estadisticas['total_reportes'],
                'validados': estadisticas['reportes_validados'],
                'pendientes': estadisticas['reportes_pendientes'],
                'credibilidad': round(estadisticas.get('promedio_credibilidad', 0))
            }
            
            context['recent_reports'] = recent_reports
            
        except (UsuarioSinReportesError, UsuarioReporteError):
            # En caso de error o sin reportes, usar valores por defecto
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
        user = self.request.user
        
        try:
            service = ReportesUsuarioService(user.id)
            
            # Obtener filtros de la URL
            filtros = {
                'estado': self.request.GET.get("estado", ""),
                'tipo_incidente': self.request.GET.get("tipo", ""),
                'fecha_desde': self.request.GET.get("fecha_desde", ""),
                'nivel_peligro': self.request.GET.get("nivel_peligro", ""),
                'solo_validados': self.request.GET.get("solo_validados") == 'true'
            }
            
            # Limpiar filtros vacíos
            filtros = {k: v for k, v in filtros.items() if v}
            
            # Obtener página actual
            pagina = self.request.GET.get('page', 1)
            
            # Obtener datos usando el servicio
            resultado = service.obtener_reportes_usuario(filtros=filtros, pagina=pagina)
            
            # Actualizar contexto con los resultados
            context.update(resultado)
            
            # Agregar opciones para los filtros
            context['estados_reporte'] = [
                ('pendiente', 'Pendiente'),
                ('validado', 'Validado'),
                ('rechazado', 'Rechazado'),
                ('archivado', 'Archivado'),
            ]
            
            context['tipos_incidente'] = [
                ('accidente', 'Accidente'),
                ('congestion', 'Congestión'),
                ('obra', 'Obra en construcción'),
                ('manifestacion', 'Manifestación'),
                ('vehiculo_varado', 'Vehículo varado'),
                ('otro', 'Otro'),
            ]
            
            context['niveles_peligro'] = [
                (1, 'Bajo'),
                (2, 'Medio'),
                (3, 'Alto'),
            ]
            
        except UsuarioSinReportesError:
            # Usuario sin reportes
            context['reportes'] = []
            context['estadisticas'] = {
                'total_reportes': 0,
                'reportes_validados': 0,
                'reportes_pendientes': 0,
                'tasa_validacion': 0,
            }
            context['filtros_aplicados'] = {}
            context['estados_reporte'] = []
            context['tipos_incidente'] = []
            context['sin_reportes'] = True
            
        except UsuarioReporteError as e:
            # Error general
            context['error'] = str(e)
            context['reportes'] = []
            context['estadisticas'] = {
                'total_reportes': 0,
                'reportes_validados': 0,
                'reportes_pendientes': 0,
                'tasa_validacion': 0,
            }
            
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
            reporte = get_object_or_404(Reporte, id=reporte_id)
            
            # Verificar permisos
            if reporte.usuario_reportador != user and not user.is_superuser:
                context['error'] = "No tienes permisos para ver este reporte"
            else:
                # Calcular datos adicionales del reporte
                total_votos = reporte.votos_positivos + reporte.votos_negativos
                if total_votos > 0:
                    reporte.credibilidad_porcentaje = round((reporte.votos_positivos * 100) / total_votos)
                else:
                    reporte.credibilidad_porcentaje = 0
                
                context['reporte'] = reporte
                
        except Exception as e:
            context['error'] = "Error al cargar el reporte"
            
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


# Vista adicional para crear reportes (si no la tienes)
class ReportIncidentView(LoginRequiredMixin, TemplateView):
    template_name = 'report_incident.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['tipos_incidente'] = [
            ('accidente', 'Accidente'),
            ('congestion', 'Congestión'),
            ('obra', 'Obra en construcción'),
            ('manifestacion', 'Manifestación'),
            ('vehiculo_varado', 'Vehículo varado'),
            ('otro', 'Otro'),
        ]
        
        context['niveles_peligro'] = [
            (1, 'Bajo'),
            (2, 'Medio'),
            (3, 'Alto'),
        ]
        
        return context


# Tus vistas existentes (mantenidas)
def home(request):
    return render(request, 'home.html')

def register(request):
    return render(request, 'register.html')

def test(request):
    return render(request, 'test.html')

#login admin / django
@csrf_protect
def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            response = redirect('/panel/')
            return response
        else:
            messages.error(request, 'Credenciales inválidas o no eres superusuario.')
    return render(request, 'login_admin.html')

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
@never_cache
def admin_reportes(request):
    controlador = ReporteColaborativoController()

    estado = request.GET.get("estado", "")
    fecha = request.GET.get("fecha", "")
    ubicacion = request.GET.get("ubicacion", "")

    reportes = controlador.obtener_todos()

    if estado:
        reportes = [r for r in reportes if r.estado_reporte == estado]
    if fecha:
        reportes = [r for r in reportes if r.fecha_creacion == fecha]
    if ubicacion:
        reportes = [r for r in reportes if r.ubicacion == ubicacion]

    return render(request, 'partials/admin_reportes.html', {
        "titulo": "Control de Reportes",
        "reportes": reportes,
        "estado_actual": estado,
        "fecha_actual": fecha,
        "ubicacion_actual": ubicacion
    })

# class button conectet
class PlanRouteView(TemplateView):
    template_name = 'plan_route.html'

class ReporteIncidentView(CreateView):
    model = ReporteColaborativo
    form_class = ReporteColaborativoForm
    template_name = 'report_incident.html'
    success_url = reverse_lazy('dashboard')  # Cambia esto según tu vista destino

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.usuario_reportador = self.request.user
        else:
            # defensa ante un mal uso 
            form.add_error(None, "Debes iniciar sesión para enviar un reporte.")
            return self.form_invalid(form)
        return super().form_valid(form)


class SeeStateView(TemplateView):
    template_name = 'see_state.html'