from django.urls import path
from .views import admin_reportes, logout_admin, custom_login, panel_personalizado, editar_reporte
from django.contrib import admin

urlpatterns = [
    path("loginadmin/", custom_login, name="custom_login"),
    path("logout_admin/", logout_admin, name="logout_admin"),
    path("panel/reportes/", admin_reportes, name="admin_reportes"),
    path("panel/editar/<int:id>/", editar_reporte, name="editar_reporte"),
    path("admin/", admin.site.urls),
    path("panel/", panel_personalizado, name="panel_personalizado"),
]
