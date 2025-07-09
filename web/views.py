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
from .forms import RegistroUsuarioForm, LoginForm
from app.presentation.controladores.reporteColaborativoController import ReporteColaborativoController
##Reporte imports
from .models import ReporteColaborativo
from .forms import ReporteColaborativoForm


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

class ReportIncidentView(TemplateView):
    template_name = 'report_incident.html'

class SeeStateView(TemplateView):
    template_name = 'see_state.html'


##implementacion en vista de el reporte colaborativo.
@login_required
def lista_reportes(request):
    reportes = ReporteColaborativo.objects.order_by('-fecha_creacion')[:4]
    return render(request, 'reportes/lista.html', {'reportes': reportes})

@login_required
def agregar_reporte(request):
    if request.method == 'POST':
        form = ReporteColaborativoForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.usuario_reportador = request.user
            reporte.save()
            messages.success(request, "Reporte enviado correctamente.")
            return redirect('lista_reportes')
    else:
        form = ReporteColaborativoForm()
    return render(request, 'reportes/agregar.html', {'form': form})

@login_required
def eliminar_reporte(request, id):
    reporte = get_object_or_404(ReporteColaborativo, id=id)
    if request.user == reporte.usuario_reportador or request.user.is_staff:
        reporte.delete()
        messages.success(request, "Reporte eliminado.")
    else:
        messages.error(request, "No tienes permiso para eliminar este reporte.")
    return redirect('lista_reportes')
