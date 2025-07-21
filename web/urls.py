from django.urls import path
from . import views
from .views import admin_reportes, LoginView, custom_login

app_name = 'reportes'

urlpatterns = [
    # ============ RUTAS BÁSICAS ============
    path('', views.home, name='home'),
    path('test/', views.test, name='test'),
    
    # ============ AUTENTICACIÓN ============
    path('register/', views.RegistroUsuarioView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ============ ADMIN ============
    path('loginadmin/', custom_login, name='custom_login'),
    path('logout_admin/', views.logout_admin, name='logout_admin'),
    path('panel/', views.panel_personalizado, name='panel_personalizado'),
    path('panel/reportes/', admin_reportes, name='admin_reportes'),
    
    # ============ DASHBOARD Y FUNCIONALIDADES PRINCIPALES ============
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('plan_route/', views.PlanRouteView.as_view(), name='plan_route'),
    path('report_incident/', views.ReporteIncidentView.as_view(), name='report_incident'),
    path('see_state/', views.SeeStateView.as_view(), name='see_state'),
    
    # ============ GESTIÓN DE REPORTES USUARIO ============
    path('mis-reportes/', views.mis_reportes_view, name='mis_reportes'),
    path('reportes/detalle/<int:reporte_id>/', views.detalle_reporte_view, name='detalle_reporte'),
    path('reportes/crear/', views.crear_reporte_view, name='crear_reporte'),
    path('reportes/editar/<int:reporte_id>/', views.editar_reporte_view, name='editar_reporte'),
    path('reportes/eliminar/<int:reporte_id>/', views.eliminar_reporte_view, name='eliminar_reporte'),
    path('reportes/votar/<int:reporte_id>/', views.votar_reporte_view, name='votar_reporte'),
    path('reportes/exportar/', views.exportar_reportes_view, name='exportar_reportes'),
    
    # ============ APIs RESTful ============
    path('api/mis-reportes/', views.api_mis_reportes, name='api_mis_reportes'),
    path('api/reporte/<int:reporte_id>/', views.api_detalle_reporte, name='api_detalle_reporte'),
    path('api/estadisticas/', views.api_estadisticas_usuario, name='api_estadisticas_usuario'),
    path('api/crear/', views.api_crear_reporte, name='api_crear_reporte'),
    path('api/votar/<int:reporte_id>/', views.api_votar_reporte, name='api_votar_reporte'),
    path('api/exportar/', views.api_exportar_reportes, name='api_exportar_reportes'),
]