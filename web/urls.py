# urls.py
from django.urls import path
from . import views
from .views import admin_reportes, LoginView, custom_login

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.RegistroUsuarioView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'), 
    path('loginadmin/', custom_login, name='custom_login'),  
    path('logout/', views.logout_view, name='logout'), 
    path('logout_admin/', views.logout_admin, name='logout_admin'),  
    path('panel/reportes/', admin_reportes, name='admin_reportes'),  
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),  
    path('test/', views.test, name='test'),  
    path('plan_route/', views.PlanRouteView.as_view(), name='plan_route'),
    path('report_incident/', views.ReporteIncidentView.as_view(), name='report_incident'),
    path('see_state/', views.SeeStateView.as_view(), name='see_state'),
    path('mis_reportes/', views.MisReportesView.as_view(), name='mis_reportes'),
    path('reporte/<int:reporte_id>/', views.DetalleReporteView.as_view(), name='detalle_reporte'),
]
