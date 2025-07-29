
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.RegistroUsuarioView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("mapa-calor/", views.vista_mapa_calor, name="mapa_calor"),
    path("mapa-embebido/", views.mapa_embebido_view, name="mapa_embebido"),
    path("plan-route/", views.PlanRouteView.as_view(), name="plan_route"),
    path("report-incident/", views.ReporteIncidentView.as_view(), name="report_incident"),
    path("see-state/", views.SeeStateView.as_view(), name="see_state"),
    path("estado-trafico/", views.estado_trafico, name="estado_trafico"),

    # APIs para notificaciones de tráfico
    path('api/ubicacion/actualizar/', views.actualizar_ubicacion, name='api_actualizar_ubicacion'),
    path('api/notificaciones/cercanas/', views.obtener_notificaciones_cercanas, name='api_notificaciones_cercanas'),
    path('api/notificaciones/config/', views.obtener_configuracion_notificaciones, name='api_config_notificaciones'),
    path('api/notificaciones/config/actualizar/', views.actualizar_configuracion_notificaciones, name='api_actualizar_config'),
    path('api/notificaciones/estadisticas/', views.obtener_estadisticas_notificaciones, name='api_estadisticas_notificaciones'),
    path('configuracion/notificaciones/', views.configuracion_notificaciones, name='configuracion_notificaciones'),

    # Vista de configuración de notificaciones
    path('notificaciones/config/', views.configuracion_notificaciones, name='configuracion_notificaciones'),
]
