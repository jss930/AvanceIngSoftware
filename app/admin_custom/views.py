# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import user_passes_test  
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from functools import wraps
import logging
from app.presentation.controladores.reporteColaborativoController import ReporteColaborativoController
from .forms import AlertaForm
from .models import Alerta
from app.presentation.controladores.alertaController import obtener_alertas_usuario

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


def validar_longitud(valor, campo, min=1, max=255):
    """Valida la longitud de un campo"""
    if not valor or len(valor) < min:
        raise ValidationError(f"El campo {campo} debe tener al menos {min} caracteres.")
    if len(valor) > max:
        raise ValidationError(f"El campo {campo} no puede exceder {max} caracteres.")
    return True


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
    - Distrito/Nombre de vía
    """
    controlador = ReporteColaborativoController()

    # Sanitiza parámetros de búsqueda
    estado = sanitizar_input(request.GET.get("estado"))
    fecha = sanitizar_input(request.GET.get("fecha"))
    filtro_ubicacion = sanitizar_input(request.GET.get("ubicacion"))  # Mantenemos 'ubicacion' para compatibilidad con el template

    try:
        reportes = controlador.obtener_todos()
        
        # Filtrado seguro
        if estado:
            reportes = [r for r in reportes if r.estado_reporte.lower() == estado.lower()]
        if fecha:
            reportes = [r for r in reportes if str(r.fecha_creacion) == fecha]
        if filtro_ubicacion:
            reportes = [r for r in reportes if filtro_ubicacion.lower() in (r.nombre_via or '').lower() or filtro_ubicacion.lower() in (r.distrito or '').lower()]

        context = {
            "titulo": "Control de Reportes",
            "reportes": reportes,
            "estado_actual": estado,
            "fecha_actual": fecha,
            "ubicacion_actual": filtro_ubicacion
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
        nombre_via = request.POST.get("nombre_via", "").strip()
        distrito = request.POST.get("distrito", "").strip()
        tipo_incidente = request.POST.get("tipo_incidente", "").strip()
        estado_reporte = request.POST.get("estado_reporte", "").strip()
        nivel_peligro = request.POST.get("nivel_peligro", "1")
        latitud = request.POST.get("latitud")
        longitud = request.POST.get("longitud")
        is_active = request.POST.get("is_active") == "on"
        nueva_foto = request.FILES.get("foto")

        # Validación
        if not titulo or not descripcion or not tipo_incidente or not estado_reporte:
            messages.error(request, "Los campos título, descripción, tipo de incidente y estado son obligatorios.")
        else:
            try:
                # Actualiza atributos básicos
                reporte.titulo = titulo
                reporte.descripcion = descripcion
                reporte.nombre_via = nombre_via
                reporte.distrito = distrito
                reporte.tipo_incidente = tipo_incidente
                reporte.estado_reporte = estado_reporte
                reporte.nivel_peligro = int(nivel_peligro)
                reporte.is_active = is_active
                
                # Actualizar coordenadas si se proporcionan
                if latitud and longitud:
                    from decimal import Decimal
                    reporte.latitud = Decimal(str(latitud))
                    reporte.longitud = Decimal(str(longitud))
                
                # Manejar nueva imagen si se proporciona
                if nueva_foto:
                    # Validar tamaño de imagen
                    if nueva_foto.size > 5 * 1024 * 1024:  # 5MB
                        messages.error(request, "La imagen no puede ser mayor a 5MB.")
                        return render(request, "partials/editar_reporte.html", {"reporte": reporte})
                    
                    # Eliminar imagen anterior si existe
                    if hasattr(reporte, 'foto') and reporte.foto:
                        try:
                            import os
                            if os.path.exists(reporte.foto.path):
                                os.remove(reporte.foto.path)
                        except:
                            pass  # Si hay error eliminando, continuar
                    
                    # Asignar nueva imagen
                    reporte.foto = nueva_foto

                # Guarda cambios usando el nuevo método
                controlador.actualizar_reporte_completo(id, reporte)
                messages.success(request, "Reporte actualizado correctamente.")
                logger.info(f"Reporte {id} actualizado por admin {request.user}")
                return redirect("admin_reportes")
                
            except Exception as e:
                logger.error(f"Error actualizando reporte {id}: {str(e)}")
                messages.error(request, f"Error al actualizar el reporte: {str(e)}")

    return render(request, "partials/editar_reporte.html", {
        "reporte": reporte
    })


@admin_required
def cambiar_estado_reporte(request, id):
    """Cambia el estado de un reporte (aceptar/rechazar)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        import json
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        
        if nuevo_estado not in ['probado', 'rechazado']:
            return JsonResponse({'success': False, 'error': 'Estado no válido'})
        
        controlador = ReporteColaborativoController()
        reporte = controlador.obtener_reporte(id)
        
        if not reporte:
            return JsonResponse({'success': False, 'error': 'Reporte no encontrado'})
        
        # Actualizar estado
        reporte.estado_reporte = nuevo_estado
        controlador.actualizar_reporte_completo(id, reporte)
        
        logger.info(f"Estado cambiado para reporte {id}: {nuevo_estado} por {request.user}")
        return JsonResponse({'success': True, 'mensaje': 'Estado actualizado correctamente'})
        
    except Exception as e:
        logger.error(f"Error cambiando estado reporte {id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
def gestionar_alertas(request):
    alertas = Alerta.objects.all().order_by('-fecha_envio')
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
