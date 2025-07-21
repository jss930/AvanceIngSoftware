# views.py
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import transaction
from datetime import datetime, timedelta
import json
import csv
from io import StringIO

# Importaciones de tu proyecto
from .forms import RegistroUsuarioForm, LoginForm, ReporteColaborativoForm
from app.presentation.controladores.reporteColaborativoController import ReporteColaborativoController
from .models import ReporteColaborativo
from web.models import Reporte

REPORTE_NO_ENCONTRADO = 'Reporte no encontrado'

# ============ FUNCIONES DE UTILIDAD ============
def is_superuser(user):
    return user.is_authenticated and user.is_superuser

# ============ VISTAS BÁSICAS ============
def home(request):
    return render(request, 'home.html')

def test(request):
    return render(request, 'test.html')

# ============ AUTENTICACIÓN ============
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

# ============ ADMIN ============
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

def logout_admin(request):
    logout(request)
    return redirect('custom_login')

@login_required(login_url='/loginadmin/')
@user_passes_test(is_superuser, login_url='/loginadmin/')
@never_cache
def panel_personalizado(request):
    context = {'titulo': 'Panel Administrativo'}
    return render(request, 'panel/personalizado.html', context)

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

# ============ DASHBOARD Y FUNCIONALIDADES PRINCIPALES ============
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class PlanRouteView(LoginRequiredMixin, TemplateView):
    template_name = 'plan_route.html'
    login_url = 'login'

class ReporteIncidentView(LoginRequiredMixin, CreateView):
    model = ReporteColaborativo
    form_class = ReporteColaborativoForm
    template_name = 'report_incident.html'
    success_url = reverse_lazy('dashboard')
    login_url = 'login'

    def form_valid(self, form):
        form.instance.usuario_reportador = self.request.user
        messages.success(self.request, '¡Reporte enviado exitosamente!')
        return super().form_valid(form)

class SeeStateView(LoginRequiredMixin, TemplateView):
    template_name = 'see_state.html'
    login_url = 'login'

# ============ VISTAS DE REPORTES (USANDO EL CÓDIGO DE REPORTESUSUARIO.PY) ============

@login_required
def mis_reportes_view(request):
    """Vista principal para mostrar los reportes del usuario"""
    try:
        # Usar pipeline para procesar la solicitud
        pipeline = ReportesDataPipeline()
        pipeline.agregar_paso(validar_usuario_reportes) \
                .agregar_paso(cargar_reportes_usuario) \
                .agregar_paso(aplicar_filtros) \
                .agregar_paso(cargar_estadisticas)
        
        # Obtener filtros de la URL
        filtros = {
            'estado': request.GET.get('estado'),
            'tipo_incidente': request.GET.get('tipo'),
            'fecha_desde': request.GET.get('fecha_desde')
        }
        
        data = {
            'usuario_id': request.user.id,
            'filtros': {k: v for k, v in filtros.items() if v}
        }
        
        resultado = pipeline.procesar(data)
        
        # Paginación
        paginator = Paginator(resultado['reportes_filtrados'], 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'reportes': page_obj,
            'estadisticas': resultado['estadisticas'],
            'filtros_aplicados': filtros,
            'tipos_incidente': Reporte.TIPOS_INCIDENTE,
            'estados_reporte': Reporte.ESTADOS_REPORTE,
        }
        
        return render(request, 'reportes/mis_reportes.html', context)
        
    except Exception:
        messages.error(request, 'Error al cargar los reportes')
        context = {
            'error': 'Error al cargar los reportes',
            'reportes': [],
            'estadisticas': {},
            'tipos_incidente': Reporte.TIPOS_INCIDENTE,
            'estados_reporte': Reporte.ESTADOS_REPORTE,
        }
        return render(request, 'reportes/mis_reportes.html', context)

@login_required
def detalle_reporte_view(request, reporte_id):
    """Vista para mostrar el detalle de un reporte"""
    try:
        detalle_thing = ReporteDetalleThing(reporte_id)
        detalles = detalle_thing.obtener_detalles_completos()
        
        # Verificar permisos
        if detalles['reporte'].usuario_reportador != request.user:
            raise SinPermisosReporteError("No tienes permisos para ver este reporte")
        
        context = {
            'reporte': detalles['reporte'],
            'credibilidad': detalles['credibilidad'],
            'total_votos': detalles['total_votos'],
            'puede_editar': detalles['puede_editar'],
            'es_reciente': detalles['es_reciente'],
            'ubicacion_texto': detalles['ubicacion_texto']
        }
        
        return render(request, 'reportes/detalle_reporte.html', context)
        
    except ReporteNoEncontradoError:
        messages.error(request, REPORTE_NO_ENCONTRADO)
        return redirect('mis_reportes')
    except SinPermisosReporteError:
        messages.error(request, 'No tienes permisos para ver este reporte')
        return redirect('mis_reportes')

@login_required
def crear_reporte_view(request):
    """Vista para crear un nuevo reporte"""
    if request.method == 'POST':
        form = ReporteColaborativoForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.usuario_reportador = request.user
            reporte.save()
            messages.success(request, '¡Reporte creado exitosamente!')
            return redirect('detalle_reporte', reporte_id=reporte.id)
    else:
        form = ReporteColaborativoForm()
    
    return render(request, 'reportes/crear_reporte.html', {'form': form})

@login_required
def editar_reporte_view(request, reporte_id):
    """Vista para editar un reporte existente"""
    try:
        reporte = get_object_or_404(Reporte, id=reporte_id, usuario_reportador=request.user)
        
        # Verificar si puede editarse
        if reporte.estado_reporte != 'pendiente':
            messages.error(request, 'No puedes editar este reporte')
            return redirect('detalle_reporte', reporte_id=reporte_id)
        
        if request.method == 'POST':
            form = ReporteColaborativoForm(request.POST, request.FILES, instance=reporte)
            if form.is_valid():
                form.save()
                messages.success(request, '¡Reporte actualizado exitosamente!')
                return redirect('detalle_reporte', reporte_id=reporte_id)
        else:
            form = ReporteColaborativoForm(instance=reporte)
        
        return render(request, 'reportes/editar_reporte.html', {
            'form': form,
            'reporte': reporte
        })
    
    except Reporte.DoesNotExist:
        messages.error(request, REPORTE_NO_ENCONTRADO)
        return redirect('mis_reportes')

@login_required
@require_POST
def eliminar_reporte_view(request, reporte_id):
    """Vista para eliminar un reporte"""
    try:
        reporte = get_object_or_404(Reporte, id=reporte_id, usuario_reportador=request.user)
        
        if reporte.estado_reporte != 'pendiente':
            messages.error(request, 'No puedes eliminar este reporte')
        else:
            titulo_reporte = reporte.titulo
            reporte.delete()
            messages.success(request, f'Reporte "{titulo_reporte}" eliminado exitosamente')
        
        return redirect('mis_reportes')
    
    except Reporte.DoesNotExist:
        messages.error(request, REPORTE_NO_ENCONTRADO)
        return redirect('mis_reportes')

@login_required
@require_POST
def votar_reporte_view(request, reporte_id):
    """Vista para votar por un reporte"""
    try:
        reporte = get_object_or_404(Reporte, id=reporte_id)
        voto_positivo = request.POST.get('voto') == 'positivo'
        
        # No permitir votar en sus propios reportes
        if reporte.usuario_reportador == request.user:
            messages.error(request, 'No puedes votar en tus propios reportes')
            return redirect('detalle_reporte', reporte_id=reporte_id)
        
        with transaction.atomic():
            # Crear o actualizar voto
            voto, created = VotoReporte.objects.get_or_create(
                reporte=reporte,
                usuario_votante=request.user,
                defaults={'voto_positivo': voto_positivo}
            )
            
            if not created:
                # Si ya existía, actualizar
                voto.voto_positivo = voto_positivo
                voto.save()
            
            # Recalcular contadores
            votos_positivos = VotoReporte.objects.filter(reporte=reporte, voto_positivo=True).count()
            votos_negativos = VotoReporte.objects.filter(reporte=reporte, voto_positivo=False).count()
            
            reporte.votos_positivos = votos_positivos
            reporte.votos_negativos = votos_negativos
            reporte.save()
        
        tipo_voto = "positivo" if voto_positivo else "negativo"
        messages.success(request, f'Tu voto {tipo_voto} ha sido registrado')
        
        return redirect('detalle_reporte', reporte_id=reporte_id)
    
    except Reporte.DoesNotExist:
        messages.error(request, REPORTE_NO_ENCONTRADO)
        return redirect('mis_reportes')

@login_required
def exportar_reportes_view(request):
    """Vista para exportar reportes a CSV"""
    try:
        visualizador = ReporteVisualizadorThing(request.user.id)
        reportes = visualizador.reportes
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="mis_reportes_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Título', 'Descripción', 'Tipo Incidente', 'Estado',
            'Nivel Peligro', 'Fecha Creación', 'Votos Positivos', 'Votos Negativos'
        ])
        
        for reporte in reportes:
            writer.writerow([
                reporte.id,
                reporte.titulo,
                reporte.descripcion,
                reporte.get_tipo_incidente_display(),
                reporte.get_estado_reporte_display(),
                reporte.nivel_peligro,
                reporte.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
                reporte.votos_positivos,
                reporte.votos_negativos
            ])
        
        return response
    
    except Exception:
        messages.error(request, 'Error al exportar reportes')
        return redirect('mis_reportes')

# ============ API VIEWS ============
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_mis_reportes(request):
    """API para obtener reportes del usuario"""
    try:
        pipeline = ReportesDataPipeline()
        pipeline.agregar_paso(validar_usuario_reportes) \
                .agregar_paso(cargar_reportes_usuario) \
                .agregar_paso(aplicar_filtros) \
                .agregar_paso(cargar_estadisticas) \
                .agregar_paso(formatear_respuesta_reportes)
        
        filtros = {
            'estado': request.GET.get('estado'),
            'tipo_incidente': request.GET.get('tipo'),
            'fecha_desde': request.GET.get('fecha_desde')
        }
        
        data = {
            'usuario_id': request.user.id,
            'filtros': {k: v for k, v in filtros.items() if v}
        }
        
        resultado = pipeline.procesar(data)
        return Response(resultado, status=status.HTTP_200_OK)
        
    except Exception:
        return Response(
            {'error': 'Error al obtener reportes'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_detalle_reporte(request, reporte_id):
    """API para obtener detalle de un reporte"""
    try:
        detalle_thing = ReporteDetalleThing(reporte_id)
        reporte = detalle_thing.reporte
        
        if reporte.usuario_reportador != request.user:
            raise SinPermisosReporteError("No tienes permisos para ver este reporte")
        
        detalles = detalle_thing.obtener_detalles_completos()
        serializer = ReporteSerializer(reporte)
        
        return Response({
            'reporte': serializer.data,
            'credibilidad': detalles['credibilidad'],
            'puede_editar': detalles['puede_editar'],
            'es_reciente': detalles['es_reciente'],
            'ubicacion_texto': detalles['ubicacion_texto']
        }, status=status.HTTP_200_OK)
        
    except ReporteNoEncontradoError:
        return Response({'error': REPORTE_NO_ENCONTRADO}, status=status.HTTP_404_NOT_FOUND)
    except SinPermisosReporteError:
        return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_estadisticas_usuario(request):
    """API para obtener estadísticas del usuario"""
    try:
        visualizador = ReporteVisualizadorThing(request.user.id)
        estadisticas = visualizador.obtener_estadisticas_usuario()
        return Response(estadisticas, status=status.HTTP_200_OK)
    except Exception:
        return Response({'error': 'Error al obtener estadísticas'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_crear_reporte(request):
    """API para crear un nuevo reporte"""
    try:
        serializer = ReporteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario_reportador=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({'error': 'Error al crear reporte'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_votar_reporte(request, reporte_id):
    """API para votar por un reporte"""
    try:
        reporte = get_object_or_404(Reporte, id=reporte_id)
        voto_positivo = request.data.get('voto_positivo', True)
        
        if reporte.usuario_reportador == request.user:
            return Response({'error': 'No puedes votar tus propios reportes'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            voto, created = VotoReporte.objects.get_or_create(
                reporte=reporte,
                usuario_votante=request.user,
                defaults={'voto_positivo': voto_positivo}
            )
            
            if not created:
                voto.voto_positivo = voto_positivo
                voto.save()
            
            # Recalcular contadores
            votos_positivos = VotoReporte.objects.filter(reporte=reporte, voto_positivo=True).count()
            votos_negativos = VotoReporte.objects.filter(reporte=reporte, voto_positivo=False).count()
            
            reporte.votos_positivos = votos_positivos
            reporte.votos_negativos = votos_negativos
            reporte.save()
        
        return Response({'message': 'Voto registrado exitosamente'}, status=status.HTTP_200_OK)
    
    except Reporte.DoesNotExist:
        return Response({'error': REPORTE_NO_ENCONTRADO}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_exportar_reportes(request):
    """API para exportar reportes"""
    try:
        visualizador = ReporteVisualizadorThing(request.user.id)
        reportes = visualizador.reportes
        
        reportes_data = []
        for reporte in reportes:
            reportes_data.append({
                'id': reporte.id,
                'titulo': reporte.titulo,
                'descripcion': reporte.descripcion,
                'tipo_incidente': reporte.get_tipo_incidente_display(),
                'estado': reporte.get_estado_reporte_display(),
                'nivel_peligro': reporte.nivel_peligro,
                'fecha_creacion': reporte.fecha_creacion,
                'votos_positivos': reporte.votos_positivos,
                'votos_negativos': reporte.votos_negativos
            })
        
        return Response({
            'reportes': reportes_data,
            'total': len(reportes_data),
            'usuario': request.user.username
        }, status=status.HTTP_200_OK)
    
    except Exception:
        return Response({'error': 'Error al exportar'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)