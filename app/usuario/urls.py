
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.RegistroUsuarioView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("mis-reportes/", views.MisReportesView.as_view(), name="mis_reportes"),
    path('mis_reportes/', views.MisReportesView.as_view(), name='mis_reportes'),
    path('reporte/<int:reporte_id>/', views.DetalleReporteView.as_view(), name='detalle_reporte'),
    path('configuracion/', views.vista_configuracion_usuario, name='configuracion_usuario'),    
    path('reporte/<int:pk>/editar/', views.EditarReporteView.as_view(), name='editar_reporte'),
    path('reportes/validar/<int:reporte_id>/', views.DetalleReporteView.as_view(), name='validar_reporte'),
    path('reporte/<int:pk>/eliminar/', views.EliminarReporteView.as_view(), name='eliminar_reporte'),
    path("mapa-calor/", views.vista_mapa_calor, name="mapa_calor"),
    path("mapa-embebido/", views.mapa_embebido_view, name="mapa_embebido"),
    path("plan-route/", views.PlanRouteView.as_view(), name="plan_route"),
    path("report-incident/", views.ReporteIncidentView.as_view(), name="report_incident"),
    path("see-state/", views.SeeStateView.as_view(), name="see_state"),

    #path('login/', LoginView.as_view(), name='login'), 
    #path('loginadmin/', custom_login, name='custom_login'), 
    path('logout_admin/', views.logout_admin, name='logout_admin'),
    #path('panel/reportes/', admin_reportes, name='admin_reportes'), 
    path('test/', views.test, name='test'),  
    path('plan_route/', views.PlanRouteView.as_view(), name='plan_route'),
]
