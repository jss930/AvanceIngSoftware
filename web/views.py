from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from .forms import RegistroUsuarioForm, LoginForm, ReporteColaborativoForm, AlertaForm
from .models import ReporteColaborativo, Alerta
from app.presentation.controladores.reporteColaborativoController import ReporteColaborativoController
from app.presentation.controladores.alertaController import obtener_alertas_usuario
from app.dominio.mapa_calor.generador_mapa import generar_mapa_calor
import os
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

# Dashboard como Class-Based View
@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class DashboardView(LoginRequiredMixin, FormView):
    template_name = 'dashboard.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        alertas = obtener_alertas_usuario(request.user.id)  
        return render(request, self.template_name, {
            'user': request.user,
            'alertas': alertas
        })
# Mapa de calor funcion
def vista_mapa(request):
    print("✅ Entrando a vista_mapa...")

    reportes = [
        {"latitud": -16.4091, "longitud": -71.5375, "estado": "congestionado"},
        {"latitud": -16.4100, "longitud": -71.5360, "estado": "fluido"},
        {"latitud": -16.4080, "longitud": -71.5380, "estado": "congestionado"}
    ]

    mapa = generar_mapa_calor(reportes)

    ruta_mapa = os.path.abspath("web/static/mapa_calor.html")
    mapa.save(ruta_mapa)
    print("✅ Mapa guardado en:", ruta_mapa)

    try:
        with open(ruta_mapa, "r", encoding="utf-8") as f:
            mapa_html = f.read()
        print("HTML del mapa leído correctamente")
    except Exception as e:
        print("ERROR leyendo mapa:", e)
        mapa_html = "<p>Error al cargar el mapa</p>"

    return render(request, "mapa_calor.html", {"mapa_html": mapa_html})


# Tus vistas existentes (mantenidas)
def home(request):
    return render(request, 'home.html')

def register(request):
    return render(request, 'register.html')

def test(request):
    return render(request, 'test.html')

# login admin / django
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

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
def crear_alerta(request):
    if request.method == 'POST':
        form = AlertaForm(request.POST)
        if form.is_valid():
            titulo = form.cleaned_data['titulo']
            mensaje = form.cleaned_data['mensaje']
            ubicacion = form.cleaned_data['ubicacion']

            if request.POST.get("enviar_a_todos"):
                destinatarios = User.objects.filter(is_active=True)
            else:
                destinatarios_ids = request.POST.getlist("destinatarios")
                destinatarios = User.objects.filter(id__in=destinatarios_ids)

            from app.presentation.controladores.alertaController import emitir_alerta
            emitir_alerta(titulo, mensaje, request.user, destinatarios, ubicacion)

            messages.success(request, 'Alerta enviada con éxito.')
            return redirect('crear_alerta')
    else:
        form = AlertaForm()

    return render(request, 'panel/crear_alerta.html', {'form': form, 'titulo': 'Crear Alerta'})

# Vistas para botones del home
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

# Implementación en vista de el reporte colaborativo.
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
