
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
]
