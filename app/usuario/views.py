from app.reporte.models import ReporteColaborativo
from app.reporte.forms import ReporteColaborativoForm
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from app.repositorio.alerta.alertaRepositoryImpl import AlertaRepositoryImpl
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import RegistroUsuarioForm, LoginForm
# Agregar estas importaciones al archivo app/usuario/views.py existente
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from app.servicios.notificationApplicationService import NotificationApplicationService
import json
# from app.reporte.views import ReporteIncidentView
from django.conf import settings
from app.servicios.mapa_calor_service import MapaCalorService
from django.shortcuts import render
from django.views.generic import TemplateView
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


# Dashboard como Class-Based View
@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class DashboardView(LoginRequiredMixin, FormView):
    template_name = 'dashboard.html'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        alerta_repository = AlertaRepositoryImpl()
        alertas = alerta_repository.obtener_por_usuario(request.user.id)  
        return render(request, self.template_name, {
            'user': request.user,
            'alertas': alertas
        })

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

# === VISTAS PARA API DE NOTIFICACIONES ===

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def actualizar_ubicacion(request):
    """API endpoint para actualizar la ubicación del usuario"""
    try:
        data = json.loads(request.body)
        latitud = data.get('latitud')
        longitud = data.get('longitud')
        
        if not latitud or not longitud:
            return JsonResponse({
                'status': 'error',
                'message': 'Latitud y longitud son requeridos'
            }, status=400)
        
        notification_service = NotificationApplicationService()
        resultado = notification_service.actualizar_ubicacion_usuario(
            usuario_id=request.user.id,
            latitud=latitud,
            longitud=longitud
        )
        
        return JsonResponse(resultado)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def obtener_notificaciones_cercanas(request):
    """API endpoint para obtener notificaciones de zonas cercanas"""
    try:
        latitud = request.GET.get('lat')
        longitud = request.GET.get('lng')
        
        if not latitud or not longitud:
            return JsonResponse({
                'status': 'error',
                'message': 'Parámetros lat y lng son requeridos'
            }, status=400)
        
        notification_service = NotificationApplicationService()
        resultado = notification_service.verificar_zonas_congestionadas_cercanas(
            user=request.user,
            latitud=float(latitud),
            longitud=float(longitud)
        )
        
        return JsonResponse(resultado)
        
    except ValueError:
        return JsonResponse({
            'status': 'error',
            'message': 'Coordenadas inválidas'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def obtener_configuracion_notificaciones(request):
    """API endpoint para obtener la configuración de notificaciones"""
    try:
        notification_service = NotificationApplicationService()
        resultado = notification_service.obtener_configuracion_notificaciones(
            usuario_id=request.user.id
        )
        
        return JsonResponse(resultado)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def actualizar_configuracion_notificaciones(request):
    """API endpoint para actualizar la configuración de notificaciones"""
    try:
        data = json.loads(request.body)
        
        notification_service = NotificationApplicationService()
        resultado = notification_service.actualizar_configuracion_notificaciones(
            usuario_id=request.user.id,
            config=data
        )
        
        return JsonResponse(resultado)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def obtener_estadisticas_notificaciones(request):
    """API endpoint para obtener estadísticas de notificaciones"""
    try:
        notification_service = NotificationApplicationService()
        resultado = notification_service.obtener_estadisticas_notificaciones(
            usuario_id=request.user.id
        )
        
        return JsonResponse(resultado)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# Vista para la página de configuración de notificaciones
@login_required
def configuracion_notificaciones(request):
    """Vista para la página de configuración de notificaciones"""
    from app.usuario.models import PerfilUsuario
    from app.reporte.models import ReporteColaborativo
    
    perfil = PerfilUsuario.get_or_create_for_user(request.user)
    tipos_incidentes = ReporteColaborativo.INCIDENT_TYPES
    
    context = {
        'perfil': perfil,
        'tipos_incidentes': tipos_incidentes,
        'tipos_seleccionados': perfil.tipos_incidentes_notificar
    }
    
    return render(request, 'configuracion_notificaciones.html', context)

def estado_trafico(request):
    return render(request, 'estado_trafico.html')
