# urls.py
from django.urls import path
from . import views
from app.usuario.views import LoginView

urlpatterns = [
    
    path('report_incident/', views.ReporteIncidentView.as_view(), name='report_incident'),
    path('see_state/', views.SeeStateView.as_view(), name='see_state'),
    
]