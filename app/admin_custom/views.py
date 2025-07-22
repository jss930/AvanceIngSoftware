# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
from functools import wraps
import logging
from app.presentation.controladores.reporteColaborativoController import ReporteColaborativoController


# Configuración de logging
logger = logging.getLogger(__name__)

# Create your views here.
# admin

def admin_required(view_func):
    """
    Decorator que verifica:
    1. Usuario autenticado
    2. Es superusuario
    3. Evita caching
    """
    @wraps(view_func)
    @login_required(login_url='/loginadmin/')
    @never_cache
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Acceso restringido a administradores")
            logger.warning(f"Acceso no autorizado intentado por: {request.user}")
            return redirect('custom_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def sanitizar_input(valor):
    """Limpia y valida inputs básicos"""
    return valor.strip() if valor else ''


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


# Vistas
@csrf_protect
@never_cache
def custom_login(request):
    """
    Maneja el login de administradores con:
    - Validación de campos
    - Sanitización de inputs
    - Protección CSRF
    """
    if request.method == 'POST':
        username = sanitizar_input(request.POST.get('username'))
        password = sanitizar_input(request.POST.get('password'))

        try:
            validar_longitud(username, "Usuario")
            validar_longitud(password, "Contraseña", min=6)

            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                logger.info(f"Login exitoso para admin: {username}")
                return redirect('panel_personalizado')

            messages.error(request, 'Credenciales inválidas o no tiene privilegios de administrador')
            logger.warning(f"Intento fallido de login para: {username}")

        except ValidationError as e:
            messages.error(request, str(e))

    return render(request, 'login_admin.html')


@admin_required
def panel_personalizado(request):
    """Vista principal del panel administrativo"""
    context = {'titulo': 'Panel Administrativo'}
    return render(request, 'panel/personalizado.html', context)

# Logout del admin
def logout_admin(request):
    """Cierra sesión segura"""
    logger.info(f"Logout realizado por: {request.user}")
    logout(request)
    return redirect('custom_login')


@admin_required
def admin_reportes(request):
    """
    Lista reportes con capacidad de filtrado por:
    - Estado
    - Fecha
    - Ubicación
    """
    controlador = ReporteColaborativoController()

    # Sanitiza parámetros de búsqueda
    estado = sanitizar_input(request.GET.get("estado"))
    fecha = sanitizar_input(request.GET.get("fecha"))
    ubicacion = sanitizar_input(request.GET.get("ubicacion"))

    try:
        reportes = controlador.obtener_todos()
        
        # Filtrado seguro
        if estado:
            reportes = [r for r in reportes if r.estado_reporte.lower() == estado.lower()]
        if fecha:
            reportes = [r for r in reportes if str(r.fecha_creacion) == fecha]
        if ubicacion:
            reportes = [r for r in reportes if ubicacion.lower() in r.ubicacion.lower()]

        context = {
            "titulo": "Control de Reportes",
            "reportes": reportes,
            "estado_actual": estado,
            "fecha_actual": fecha,
            "ubicacion_actual": ubicacion
        }
        
        return render(request, 'partials/admin_reportes.html', context)

    except Exception as e:
        logger.error(f"Error en admin_reportes: {str(e)}")
        messages.error(request, "Error al cargar reportes")
        return redirect('panel_personalizado')


@admin_required
def editar_reporte(request, id):
    """
    Edición segura de reportes con:
    - Validación de ID
    - Sanitizacion de campos
    - Manejo de errores
    """
    controlador = ReporteColaborativoController()
    try:
        reporte = controlador.obtener_reporte(id)
        if not reporte:
            messages.error(request, "Reporte no encontrado.")
            return redirect("admin_reportes")
    except (ValueError, TypeError) as e:
        logger.error(f"Error en editar_reporte - ID: {id} - Error: {str(e)}")
        messages.error(request, f"Error al procesar el reporte: {str(e)}")
        return redirect("admin_reportes")

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        ubicacion = request.POST.get("ubicacion", "").strip()
        tipo_incidente = request.POST.get("tipo_incidente", "").strip()
        estado_reporte = request.POST.get("estado_reporte", "").strip()

        # Validación
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
            controlador.actualizar_reporte_completo(id, reporte)
            messages.success(request, "Reporte actualizado correctamente.")
            return redirect("admin_reportes")

    return render(request, "partials/editar_reporte.html", {
        "reporte": reporte
    })
