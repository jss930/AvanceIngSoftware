from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path("loginadmin/", views.custom_login, name="custom_login"),
    path("logout_admin/", views.logout_admin, name="logout_admin"),
    path("panel/reportes/", views.admin_reportes, name="admin_reportes"),
    path("panel/editar/\u003cint:id\u003e/", views.editar_reporte, name="editar_reporte"),
    path("panel/cambiar-estado/\u003cint:id\u003e/", views.cambiar_estado_reporte, name="cambiar_estado_reporte"),
    path("usuarios/", views.gestion_usuarios, name="gestion_usuarios"),
    path("admin/", admin.site.urls),
    path("panel/", views.panel_personalizado, name="panel_personalizado"),

    path('panel/alertas/', views.gestionar_alertas, name='gestionar_alertas'),
    path('panel/alertas/crear/', views.crear_alerta, name='crear_alerta'),
    path('panel/alertas/editar/\u003cint:alerta_id\u003e/', views.editar_alerta, name='editar_alerta'),
    path('panel/alertas/eliminar/\u003cint:alerta_id\u003e/', views.eliminar_alerta, name='eliminar_alerta'),
    
    path('historial-notificaciones/', views.historial_notificaciones, name='historial_notificaciones'),
    path('historial-notificaciones/exportar/', views.exportar_historial_csv, name='exportar_historial_csv'),
]

