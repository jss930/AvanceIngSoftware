# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from app.presentation.controladores.reporteColaborativoController import ReporteColaborativoController



# Create your views here.
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
def editar_reporte(request, id):
    controlador = ReporteColaborativoController()
    try:
        reporte = controlador.obtener_reporte(id)
        if not reporte:
            messages.error(request, "Reporte no encontrado.")
            return redirect("admin_reportes")
    except (ValueError, TypeError):
        messages.error(request, "ID inválido.")
        return redirect("admin_reportes")

    if request.method == "POST":
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
            controlador.actualizar_reporte_completo(id, reporte)
            messages.success(request, "Reporte actualizado correctamente.")
            return redirect("admin_reportes")

    return render(request, "partials/editar_reporte.html", {
        "reporte": reporte
    })
