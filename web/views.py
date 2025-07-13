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
from django.utils.decorators import method_decorator
from .forms import RegistroUsuarioForm, LoginForm
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
@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(never_cache, name='dispatch')
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

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
@never_cache
def editar_reporte(request):
    controlador = ReporteColaborativoController()
    reporte_id = request.GET.get('id')
    reporte = None

    if reporte_id:
        try:
            reporte_id = int(reporte_id)
            reporte = controlador.obtener_reporte(reporte_id)
        except (ValueError, TypeError):
            messages.error(request, "ID inválido.")

    if request.method == "POST" and reporte:
        titulo = request.POST.get("titulo", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        ubicacion = request.POST.get("ubicacion", "").strip()
        tipo_incidente = request.POST.get("tipo_incidente", "").strip()
        estado_reporte = request.POST.get("estado_reporte", "").strip()

        # Validación básica
        if not titulo or not descripcion or not ubicacion or not tipo_incidente or not estado_reporte:
            messages.error(request, "Todos los campos son obligatorios.")
        else:
            # Actualiza atributos
            reporte.titulo = titulo
            reporte.descripcion = descripcion
            reporte.ubicacion = ubicacion
            reporte.tipo_incidente = tipo_incidente
            reporte.estado_reporte = estado_reporte

            # Guarda cambios usando el nuevo método
            controlador.actualizar_reporte_completo(reporte_id, reporte)
            messages.success(request, "Reporte actualizado correctamente.")
            return redirect("admin_reportes")  # Reemplaza con el nombre real de tu URL

    return render(request, "partials/editar_reporte.html", {
        "reporte": reporte
    })


# class button conectet
class PlanRouteView(TemplateView):
    template_name = 'plan_route.html'

class ReportIncidentView(TemplateView):
    template_name = 'report_incident.html'

class SeeStateView(TemplateView):
    template_name = 'see_state.html'
