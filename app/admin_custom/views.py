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


@login_required(login_url="/loginadmin/")
@user_passes_test(is_superuser, login_url="/loginadmin/")
@never_cache
def editar_reporte(request, id):
    controlador = ReporteColaborativoController()
    reporte = controlador.obtener_por_id(id)

    if request.method == "POST":
        # Obtener datos del formulario
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        ubicacion = request.POST.get("ubicacion")
        tipo_incidente = request.POST.get("tipo_incidente")
        estado_reporte = request.POST.get("estado_reporte")

        # Actualizar el reporte
        reporte.titulo = titulo
        reporte.descripcion = descripcion
        reporte.ubicacion = ubicacion
        reporte.tipo_incidente = tipo_incidente
        reporte.estado_reporte = estado_reporte

        controlador.actualizar(reporte)
        messages.success(request, "Reporte actualizado exitosamente.")
        return redirect("admin_reportes")

    return render(request, "partials/editar_reporte.html", {
        "reporte": reporte,
        "titulo": "Editar Reporte"
    })
