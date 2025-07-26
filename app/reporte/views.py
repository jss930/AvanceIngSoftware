from django.shortcuts import render
from .models import ReporteColaborativo
from .forms import ReporteColaborativoForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, FormView


from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test


"""
# Create your views here.
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

"""

# NUEVA VISTA PARA REPORTAR INCIDENTES - CORREGIDA
class ReporteIncidentView(LoginRequiredMixin, FormView):
    template_name = 'report_incident.html'
    form_class = ReporteColaborativoForm
    success_url = reverse_lazy('dashboard')
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
    def form_valid(self, form):
        # Asignar el usuario actual al reporte
        reporte = form.save(commit=False)
        reporte.usuario_reportador = self.request.user
        reporte.save()
        
        messages.success(
            self.request, 
            f'¡Incidente "{reporte.titulo}" reportado exitosamente!'
        )
        print("✅ Formulario recibido en el backend")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print("❌ Errores en el formulario:")
        print(form.errors.as_json())  
        messages.error(
            self.request, 
            'Hubo errores en el formulario. Por favor, corrígelos.'
        )
        return super().form_invalid(form)

# VISTA ADICIONAL PARA AJAX (opcional - para mejor experiencia de usuario)
@login_required
@require_http_methods(["POST"])
def report_incident_ajax(request):
    """Vista para manejar reportes via AJAX"""
    try:
        form = ReporteColaborativoForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.usuario_reportador = request.user
            reporte.save()

            return JsonResponse({
                'success': True,
                'message': 'Incidente reportado exitosamente',
                'incident_id': reporte.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors,
                'message': 'Errores en el formulario'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        })