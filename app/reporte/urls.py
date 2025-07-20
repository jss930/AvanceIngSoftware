# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('report_incident/', views.ReporteIncidentView.as_view(), name='report_incident'),
]