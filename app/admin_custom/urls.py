from django.urls import path
from .views import admin_reportes, logout_admin, custom_login, panel_personalizado, editar_reporte, cambiar_estado_reporte, gestion_usuarios
from django.contrib import admin

urlpatterns = [
    path("loginadmin/", custom_login, name="custom_login"),
    path("logout_admin/", logout_admin, name="logout_admin"),
    path("panel/reportes/", admin_reportes, name="admin_reportes"),
    path("panel/editar/\u003cint:id\u003e/", editar_reporte, name="editar_reporte_admin"),
    path("usuarios/", gestion_usuarios, name="gestion_usuarios"),
    path("panel/cambiar-estado/\u003cint:id\u003e/", cambiar_estado_reporte, name="cambiar_estado_reporte"),
    path("admin/", admin.site.urls),
    path("panel/", panel_personalizado, name="panel_personalizado"),
]
