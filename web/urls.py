# urls.py
from django.urls import path
from . import views
from .views import admin_reportes, LoginView, custom_login, editar_reporte, crear_alerta, vista_mapa

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.RegistroUsuarioView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),  # Cambiado de views.home
    path('loginadmin/', custom_login, name='custom_login'),  # Login para admin
    path('logout/', views.logout_view, name='logout'),  #logout user
    path('logout_admin/', views.logout_admin, name='logout_admin'),  #logout admin
    path('panel/reportes/', admin_reportes, name='admin_reportes'),  #control reportes
    path('panel/editar/', editar_reporte, name='editar_reporte'),  #editar reportes
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),  # Nueva ruta
    path('test/', views.test, name='test'),  # Tu vista de prueba existente
    path('plan_route/', views.PlanRouteView.as_view(), name='plan_route'),
    path('report_incident/', views.ReporteIncidentView.as_view(), name='report_incident'),
    path('see_state/', views.SeeStateView.as_view(), name='see_state'),

    # Reportes colaborativos
    path('reportes/', views.lista_reportes, name='lista_reportes'),
    path('reportes/agregar/', views.agregar_reporte, name='agregar_reporte'),
    path('reportes/eliminar/<int:id>/', views.eliminar_reporte, name='eliminar_reporte'),
    # Alertas
    path('panel/crear_alerta/', crear_alerta, name='crear_alerta'),
    # Mapa de calor
    #path('ver-mapa/', vista_mapa, name='mapa_calor'),
    path("mapa-calor/", vista_mapa, name="mapa_calor"),

]
