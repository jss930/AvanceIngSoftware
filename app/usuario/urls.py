
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.RegistroUsuarioView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("mapa-calor/", views.MapaCalorView.as_view(), name="mapa_calor"),
    path("plan-route/", views.PlanRouteView.as_view(), name="plan_route"),
    path("report-incident/", views.ReporteIncidentView.as_view(), name="report_incident"),
    path("see-state/", views.SeeStateView.as_view(), name="see_state"),
    path('api/ubicacion/actualizar/', views.actualizar_ubicacion, name='actualizar_ubicacion'),
    path('api/notificaciones/cercanas/', views.obtener_notificaciones_cercanas, name='notificaciones_cercanas'),
    path('api/notificaciones/config/', views.obtener_configuracion_notificaciones, name='config_notificaciones'),
    path('api/notificaciones/config/actualizar/', views.actualizar_configuracion_notificaciones, name='actualizar_config_notificaciones'),
    path('api/notificaciones/estadisticas/', views.obtener_estadisticas_notificaciones, name='estadisticas_notificaciones'),
    path('configuracion/notificaciones/', views.configuracion_notificaciones, name='configuracion_notificaciones'),
]