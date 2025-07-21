from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class SeeStateView(TemplateView):
    template_name = 'see_state.html'

class PlanRouteView(TemplateView):
    template_name = 'plan_route.html'
