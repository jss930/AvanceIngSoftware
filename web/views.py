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
from web.services.mapa_calor_service import MapaCalorService
from django.conf import settings

# Nueva funcionalidad para notificaciones por ubicación
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from math import radians, cos, sin, asin, sqrt
from app.servicios.notificationApplicationService import NotificationApplicationService

import os

# ========================== PANEL ADMIN ============================

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
@never_cache
def panel_personalizado(request):
    context = {'titulo': 'Panel Administrativo'}
    return render(request, 'panel/personalizado.html', context)

def logout_admin(request):
    logout(request)
    return redirect('custom_login')

# ========================== AUTENTICACIÓN ============================

class RegistroUsuarioView(FormView):
    template_name = 'register.html'
    form_class = RegistroUsuarioForm
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"¡Bienvenido, {user.username}!")
        return super().form_valid(form)

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

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

# ========================== VISTAS PRINCIPALES ============================

@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class DashboardView(LoginRequiredMixin, FormView):
    template_name = 'dashboard.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        alertas = obtener_alertas_usuario(request.user.id)
        return render(request, self.template_name, {'user': request.user, 'alertas': alertas})

def vista_mapa(request):
    generador = MapaCalorService(settings.BASE_DIR / "web")
    path_html = generador.generar_mapa()
    try:
        with open(path_html, "r", encoding="utf-8") as file:
            html = file.read()
    except Exception as e:
        html = f"<p>Error al cargar el mapa: {e}</p>"
    return render(request, "mapa_calor_page.html", {"mapa": html})

def home(request):
    return render(request, 'home.html')

def register(request):
    return render(request, 'register.html')

def test(request):
    return render(request, 'test.html')

@csrf_protect
def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('/panel/')
        else:
            messages.error(request, 'Credenciales inválidas o no eres superusuario.')
    return render(request, 'login_admin.html')

# ========================== REPORTES ADMIN ============================

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
        if not titulo or not descripcion or not ubicacion or not tipo_incidente or not estado_reporte:
            messages.error(request, "Todos los campos son obligatorios.")
        else:
            reporte.titulo = titulo
            reporte.descripcion = descripcion
            reporte.ubicacion = ubicacion
            reporte.tipo_incidente = tipo_incidente
            reporte.estado_reporte = estado_reporte
            controlador.actualizar_reporte_completo(reporte_id, reporte)
            messages.success(request, "Reporte actualizado correctamente.")
            return redirect("admin_reportes")
    return render(request, "partials/editar_reporte.html", {"reporte": reporte})

# ========================== ALERTAS ADMIN ============================

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
def gestionar_alertas(request):
    alertas = Alerta.objects.all().order_by('-fecha_creacion')
    return render(request, 'panel/gestionar_alertas.html', {'alertas': alertas})

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

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
def editar_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, pk=alerta_id)
    if request.method == 'POST':
        form = AlertaForm(request.POST, instance=alerta)
        if form.is_valid():
            form.save()
            return redirect('gestionar_alertas')
    else:
        form = AlertaForm(instance=alerta)
    return render(request, 'panel/editar_alerta.html', {'form': form, 'alerta': alerta})

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
def eliminar_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, pk=alerta_id)
    if request.method == 'POST':
        alerta.delete()
        return redirect('gestionar_alertas')
    return render(request, 'panel/eliminar_alerta.html', {'alerta': alerta})

# ========================== REPORTES USUARIO ============================

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

class SeeStateView(TemplateView):
    template_name = 'see_state.html'

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

# ========================== H8: Recibir Ubicación y Notificar ============================

@csrf_exempt
@login_required
def recibir_ubicacion_usuario(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat_usuario = float(data.get("lat"))
            lng_usuario = float(data.get("lng"))
            usuario_id = request.user.id

            zonas = obtener_zonas_simuladas()
            for zona in zonas:
                distancia = calcular_distancia(lat_usuario, lng_usuario, zona["lat"], zona["lng"])
                if distancia <= zona["radio_km"]:
                    notif_service = NotificationApplicationService()
                    notif_service.enviar_notificacion_usuario(
                        usuario_id,
                        f"¡Zona congestionada cercana: {zona['nombre']}!",
                        tipo="alerta_trafico"
                    )
                    return JsonResponse({"mensaje": "Notificación enviada."})

            return JsonResponse({"mensaje": "No hay zonas peligrosas cerca."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)

def obtener_zonas_simuladas():
    return [
        {"nombre": "Centro Ciudad", "lat": -12.0464, "lng": -77.0428, "radio_km": 1.0},
        {"nombre": "Avenida Siempre Viva", "lat": -12.0433, "lng": -77.0283, "radio_km": 0.8},
    ]

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

@login_required
def mi_perfil(request):
    from .models import Perfil  # Asegúrate de importar esto si no está al inicio

    # Crear perfil si no existe
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        recibir = request.POST.get('recibir_notificaciones') == 'on'
        perfil.recibir_notificaciones = recibir
        perfil.save()
        messages.success(request, 'Preferencias actualizadas correctamente.')
        return redirect('mi_perfil')

    return render(request, 'mi_perfil.html', {'perfil': perfil})

