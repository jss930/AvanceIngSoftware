from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
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


# Dashboard como Class-Based View
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = 'login'  # Redirige aquí si no está autenticado
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obtener estadísticas del usuario actual
        try:
            controlador = ReporteColaborativoController()
            user_reports = [r for r in controlador.obtener_todos() if r.usuario_reportador == user]
            
            # Calcular estadísticas
            total_reportes = len(user_reports)
            validados = len([r for r in user_reports if r.estado_reporte == 'validado'])
            pendientes = len([r for r in user_reports if r.estado_reporte == 'pendiente'])
            credibilidad = round((validados / total_reportes * 100) if total_reportes > 0 else 0)
            
            context['user_stats'] = {
                'total_reportes': total_reportes,
                'validados': validados,
                'pendientes': pendientes,
                'credibilidad': credibilidad
            }
            
            # Obtener reportes recientes (últimos 5)
            recent_reports = sorted(user_reports, key=lambda x: x.fecha_creacion, reverse=True)[:5]
            context['recent_reports'] = recent_reports
            
        except Exception:
            # En caso de error, usar valores por defecto
            context['user_stats'] = {
                'total_reportes': 0,
                'validados': 0,
                'pendientes': 0,
                'credibilidad': 0
            }
            context['recent_reports'] = []
        
        # Simular usuarios online (puedes implementar esto más tarde)
        context['users_online'] = "1,247"
        
        return context


class MisReportesView(LoginRequiredMixin, TemplateView):
    template_name = 'mis_reportes.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            controlador = ReporteColaborativoController()
            # Filtrar reportes del usuario actual
            user_reports = [r for r in controlador.obtener_todos() if r.usuario_reportador == user]
            
            # Aplicar filtros de la URL si existen
            estado = self.request.GET.get("estado", "")
            if estado:
                user_reports = [r for r in user_reports if r.estado_reporte == estado]
            
            context['reportes'] = user_reports
            context['estado_actual'] = estado
            
        except Exception:
            context['reportes'] = []
            context['estado_actual'] = ""
            
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