# views.py
from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .forms import RegistroUsuarioForm, LoginForm, TrafficIncidentForm
from .models import TrafficIncident
from app.presentation.controladores.reporteColaborativoController import ReporteColaborativoController

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
class DashboardView(LoginRequiredMixin, FormView):
    template_name = 'dashboard.html'
    login_url = 'login'  # Redirige aquí si no está autenticado
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {
            'user': request.user
        })

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

# NUEVA VISTA PARA REPORTAR INCIDENTES - CORREGIDA
class ReportIncidentView(LoginRequiredMixin, FormView):
    template_name = 'report_incident.html'
    form_class = TrafficIncidentForm
    success_url = reverse_lazy('dashboard')
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
    def form_valid(self, form):
        # Asignar el usuario actual al incidente
        incident = form.save(commit=False)
        incident.user = self.request.user
        incident.save()
        
        messages.success(
            self.request, 
            f'¡Incidente "{incident.title}" reportado exitosamente!'
        )
        print("✅ Formulario recibido en el backend")
        return super().form_valid(form)
    
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
        form = TrafficIncidentForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.user = request.user
            incident.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Incidente reportado exitosamente',
                'incident_id': incident.id
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

# VISTA PARA LISTAR INCIDENTES (adicional)
class IncidentListView(LoginRequiredMixin, TemplateView):
    template_name = 'incident_list.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incidents'] = TrafficIncident.objects.filter(
            is_active=True
        ).select_related('user').order_by('-created_at')[:50]
        return context