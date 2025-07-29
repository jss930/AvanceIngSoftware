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
from django.contrib.auth.models import User
from functools import wraps
import logging
from app.presentation.controladores.reporteColaborativoController import ReporteColaborativoController
from .forms import AlertaForm
from .models import Alerta
from app.presentation.controladores.alertaController import obtener_alertas_usuario


from .models import HistorialNotificacion
from django.db.models import Q, Count
from django.core.paginator import Paginator

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


def gestion_usuarios(request):
    """
    Vista para gestionar usuarios.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Acceso restringido a administradores')
        return redirect('custom_login')

    usuarios = User.objects.all()
    return render(request, 'partials/gestion_usuarios.html', {'usuarios': usuarios})


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
    - Tipo de incidente
    - Nivel de peligro
    """
    controlador = ReporteColaborativoController()

    # Obtener parámetros de filtrado (POST o GET)
    if request.method == 'POST':
        estado = sanitizar_input(request.POST.get("estado"))
        fecha = sanitizar_input(request.POST.get("fecha"))
        filtro_ubicacion = sanitizar_input(request.POST.get("ubicacion"))
        tipo_incidente = sanitizar_input(request.POST.get("tipo_incidente"))
        nivel_peligro = sanitizar_input(request.POST.get("nivel_peligro"))
    else:
        # Para compatibilidad con GET (primera carga)
        estado = sanitizar_input(request.GET.get("estado"))
        fecha = sanitizar_input(request.GET.get("fecha"))
        filtro_ubicacion = sanitizar_input(request.GET.get("ubicacion"))
        tipo_incidente = sanitizar_input(request.GET.get("tipo_incidente"))
        nivel_peligro = sanitizar_input(request.GET.get("nivel_peligro"))

    try:
        reportes = controlador.obtener_todos()
        
        # Filtrado mejorado
        if estado:
            reportes = [r for r in reportes if r.estado_reporte.lower() == estado.lower()]
        if fecha:
            # Filtrar por fecha (formato YYYY-MM-DD)
            reportes = [r for r in reportes if str(r.fecha_creacion.date()) == fecha]
        if filtro_ubicacion:
            reportes = [r for r in reportes if filtro_ubicacion.lower() in (r.nombre_via or '').lower() or filtro_ubicacion.lower() in (r.distrito or '').lower()]
        if tipo_incidente:
            reportes = [r for r in reportes if r.tipo_incidente.lower() == tipo_incidente.lower()]
        if nivel_peligro:
            reportes = [r for r in reportes if str(r.nivel_peligro) == nivel_peligro]

        context = {
            "titulo": "Control de Reportes",
            "reportes": reportes,
            "estado_actual": estado,
            "fecha_actual": fecha,
            "ubicacion_actual": filtro_ubicacion,
            "tipo_incidente_actual": tipo_incidente,
            "nivel_peligro_actual": nivel_peligro
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

        # Validación mejorada
        if not titulo or not descripcion or not tipo_incidente or not estado_reporte:
            messages.error(request, "Los campos título, descripción, tipo de incidente y estado son obligatorios.")
        elif estado_reporte not in ['pendiente', 'probado', 'rechazado']:
            messages.error(request, "El estado del reporte no es válido.")
        else:
            try:
                # Actualizar directamente el objeto del modelo
                reporte.titulo = titulo
                reporte.descripcion = descripcion
                reporte.nombre_via = nombre_via
                reporte.distrito = distrito
                reporte.tipo_incidente = tipo_incidente
                reporte.estado_reporte = estado_reporte
                reporte.nivel_peligro = int(nivel_peligro)
                reporte.is_active = is_active
                
                # Actualizar coordenadas si se proporcionan
                try:
                    from decimal import Decimal
                    # Validar que las coordenadas no estén vacías
                    lat_str = str(latitud).strip() if latitud else ''
                    lng_str = str(longitud).strip() if longitud else ''
                    
                    # Solo actualizar si ambas coordenadas tienen valores válidos
                    if lat_str and lng_str and lat_str != '' and lng_str != '' and lat_str != 'None' and lng_str != 'None':
                        try:
                            lat_decimal = Decimal(lat_str)
                            lng_decimal = Decimal(lng_str)
                            
                            # Validar que las coordenadas estén en rangos razonables
                            if -90 <= lat_decimal <= 90 and -180 <= lng_decimal <= 180:
                                reporte.latitud = lat_decimal
                                reporte.longitud = lng_decimal
                                logger.info(f"Coordenadas actualizadas: {lat_decimal}, {lng_decimal}")
                            else:
                                logger.warning(f"Coordenadas fuera de rango: lat={lat_decimal}, lng={lng_decimal}")
                        except (ValueError, TypeError, Exception) as coord_error:
                            logger.warning(f"Error al procesar coordenadas: lat='{lat_str}', lng='{lng_str}' - {str(coord_error)}")
                    else:
                        logger.info(f"Coordenadas no válidas o vacías, manteniendo existentes: lat='{lat_str}', lng='{lng_str}'")
                except Exception as e:
                    logger.error(f"Error general en procesamiento de coordenadas: {str(e)}")
                
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
                        except Exception:
                            pass  # Si hay error eliminando, continuar
                    
                    # Asignar nueva imagen
                    reporte.foto = nueva_foto

                # Guardar directamente el modelo para asegurar que los cambios se persistan
                reporte.save()
                
                messages.success(request, "Reporte actualizado correctamente.")
                logger.info(f"Reporte {id} actualizado por admin {request.user} - Estado: {estado_reporte}, Activo: {is_active}")
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
        
        if nuevo_estado not in ['pendiente', 'probado', 'rechazado']:
            return JsonResponse({'success': False, 'error': 'Estado no válido'})
        
        controlador = ReporteColaborativoController()
        reporte = controlador.obtener_reporte(id)
        
        if not reporte:
            return JsonResponse({'success': False, 'error': 'Reporte no encontrado'})
        
        # Actualizar estado directamente
        reporte.estado_reporte = nuevo_estado
        reporte.save()
        
        logger.info(f"Estado cambiado para reporte {id}: {nuevo_estado} por {request.user}")
        return JsonResponse({'success': True, 'mensaje': 'Estado actualizado correctamente'})
        
    except Exception as e:
        logger.error(f"Error cambiando estado reporte {id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
def gestionar_alertas(request):
    alertas = Alerta.objects.all().order_by('-fecha_envio')
    
    prioridad = request.GET.get('prioridad')
    if prioridad:
        alertas = alertas.filter(prioridad=prioridad)

    activo = request.GET.get('activo')
    if activo in ['true', 'false']:
        alertas = alertas.filter(activo=(activo == 'true'))

    return render(request, 'panel/gestionar_alertas.html', {
        'alertas': alertas,
        'prioridad_actual': prioridad,
        'activo_actual': activo,
    })

def crear_alerta(request):
    if request.method == 'POST':
        form = AlertaForm(request.POST)
        if form.is_valid():
            titulo = form.cleaned_data['titulo']
            mensaje = form.cleaned_data['mensaje']
            ubicacion = form.cleaned_data['ubicacion']
            destinatarios = User.objects.filter(id__in=request.POST.getlist("destinatarios"))
            from app.presentation.controladores.alertaController import emitir_alerta
            emitir_alerta(titulo, mensaje, request.user, destinatarios, ubicacion)
            messages.success(request, 'Alerta enviada con éxito.')
            return redirect('crear_alerta')
    else:
        form = AlertaForm()
    return render(request, 'panel/crear_alerta.html', {'form': form})

def editar_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, pk=alerta_id)
    form = AlertaForm(request.POST or None, instance=alerta)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestionar_alertas')
    return render(request, 'panel/editar_alerta.html', {'form': form, 'alerta': alerta})

def eliminar_alerta(request, alerta_id):
    alerta = get_object_or_404(Alerta, pk=alerta_id)
    if request.method == 'POST':
        alerta.delete()
        return redirect('gestionar_alertas')
    return render(request, 'panel/eliminar_alerta.html', {'alerta': alerta})



# -----
@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
def historial_notificaciones(request):
    historiales = HistorialNotificacion.objects.select_related('alerta', 'usuario_destinatario').order_by('-fecha_envio_real')
    
    # Filtros opcionales
    zona = request.GET.get('zona')
    if zona:
        historiales = historiales.filter(zona__icontains=zona)
    
    return render(request, 'panel/historial_notificaciones.html', {
        'historiales': historiales,
        'zona_actual': zona,
    })
    
    
    
# --- A..
@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
def historial_notificaciones(request):
    # Obtener todos los historiales
    historiales = HistorialNotificacion.objects.select_related('alerta', 'usuario_destinatario').order_by('-fecha_envio_real')
    
    # Filtros
    zona_filtro = request.GET.get('zona', '')
    estado_filtro = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    busqueda = request.GET.get('busqueda', '')
    
    # Aplicar filtros
    if zona_filtro:
        historiales = historiales.filter(zona__icontains=zona_filtro)
    
    if estado_filtro:
        historiales = historiales.filter(estado_entrega=estado_filtro)
    
    if fecha_desde:
        from datetime import datetime
        fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
        historiales = historiales.filter(fecha_envio_real__date__gte=fecha_desde_obj)
    
    if fecha_hasta:
        from datetime import datetime
        fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        historiales = historiales.filter(fecha_envio_real__date__lte=fecha_hasta_obj)
    
    if busqueda:
        historiales = historiales.filter(
            Q(alerta__titulo__icontains=busqueda) | 
            Q(alerta__mensaje__icontains=busqueda) |
            Q(zona__icontains=busqueda)
        )
    
    
    # Estadísticas básicas
    total_envios = historiales.count()
    envios_exitosos = historiales.filter(estado_entrega='enviado').count()
    envios_fallidos = historiales.filter(estado_entrega='fallido').count()
    
    # Paginación
    paginator = Paginator(historiales, 20)  # 20 registros por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener zonas únicas para el filtro
    zonas_disponibles = HistorialNotificacion.objects.values_list('zona', flat=True).distinct().order_by('zona')
    
    context = {
        'historiales': page_obj,
        'total_envios': total_envios,
        'envios_exitosos': envios_exitosos,
        'envios_fallidos': envios_fallidos,
        'zonas_disponibles': zonas_disponibles,
        'filtros': {
            'zona': zona_filtro,
            'estado': estado_filtro,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'busqueda': busqueda,
        }
    }

    for alerta in Alerta.objects.all():
        print(f"Título: {alerta.titulo} | Mensaje: {alerta.mensaje}")
        
    print(historiales.query)

    return render(request, 'panel/historial_notificaciones.html', context)


import csv
from django.http import HttpResponse
from datetime import datetime

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
def exportar_historial_csv(request):
    # Obtener los mismos datos que en la vista del historial
    historiales = HistorialNotificacion.objects.select_related('alerta', 'usuario_destinatario').order_by('-fecha_envio_real')
    
    # Aplicar los mismos filtros que en la vista normal
    zona_filtro = request.GET.get('zona', '')
    estado_filtro = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    busqueda = request.GET.get('busqueda', '')
    
    # Aplicar filtros
    if zona_filtro:
        historiales = historiales.filter(zona__icontains=zona_filtro)
    
    if estado_filtro:
        historiales = historiales.filter(estado_entrega=estado_filtro)
    
    if fecha_desde:
        fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
        historiales = historiales.filter(fecha_envio_real__date__gte=fecha_desde_obj)
    
    if fecha_hasta:
        fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        historiales = historiales.filter(fecha_envio_real__date__lte=fecha_hasta_obj)
    
    if busqueda:
        historiales = historiales.filter(
            Q(alerta__titulo__icontains=busqueda) | 
            Q(alerta__mensaje__icontains=busqueda) |
            Q(zona__icontains=busqueda)
        )
    
    # Crear la respuesta HTTP para CSV
    response = HttpResponse(content_type='text/csv')
    fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="historial_notificaciones_{fecha_actual}.csv"'
    
    # Configurar el writer de CSV con codificación UTF-8
    response.write('\ufeff')  # BOM para UTF-8 (para Excel)
    writer = csv.writer(response)
    
    # Escribir encabezados
    writer.writerow([
        'Fecha de Envío',
        'Hora de Envío', 
        'Título de la Alerta',
        'Mensaje',
        'Zona',
        'Destinatario',
        'Estado de Entrega',
        'Tipo de Notificación',
        'Prioridad',
        'Creada por'
    ])
    
    # Escribir datos
    for historial in historiales:
        destinatario = historial.usuario_destinatario.username if historial.usuario_destinatario else "Todos los usuarios"
        
        writer.writerow([
            historial.fecha_envio_real.strftime('%d/%m/%Y'),
            historial.fecha_envio_real.strftime('%H:%M:%S'),
            historial.alerta.titulo,
            historial.alerta.mensaje,
            historial.zona,
            destinatario,
            historial.get_estado_entrega_display(),
            historial.get_tipo_notificacion_display(),
            historial.alerta.get_prioridad_display(),
            historial.alerta.enviado_por.username
        ])
    
    return response