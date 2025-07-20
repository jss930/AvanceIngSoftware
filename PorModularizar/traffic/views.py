from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import TrafficIncidentForm
from django.views.generic import TemplateView

def create_report(request):
    if request.method != 'POST':
        return render_report_form(request)

    form = TrafficIncidentForm(request.POST, request.FILES)

    if not form.is_valid():
        handle_form_errors(request, form)
        return render_report_form(request, form)

    try:
        form.save()
        messages.success(request, 'Reporte creado exitosamente')
        return redirect('traffic:dashboard')

    except ValidationError as e:
        handle_validation_errors(request, e)
    except Exception as e:
        messages.error(request, f'Error al crear el reporte: {str(e)}')

    return render_report_form(request, form)


# 🔽 Funciones auxiliares

def render_report_form(request, form=None):
    if form is None:
        form = TrafficIncidentForm()
    return render(request, 'report.html', {'form': form})

def handle_form_errors(request, form):
    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f'{field}: {error}')

def handle_validation_errors(request, exception):
    for field, errors in exception.message_dict.items():
        for error in errors:
            messages.error(request, f'{field}: {error}')

#  Clases conectar botones


class PlanRouteView(TemplateView):
    template_name = 'plan_route.html'

class ReportIncidentView(TemplateView):
    template_name = 'report_incident.html'

class SeeStateView(TemplateView):
    template_name = 'see_state.html'
