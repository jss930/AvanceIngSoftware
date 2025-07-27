from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path("loginadmin/", views.custom_login, name="custom_login"),
    path("logout_admin/", views.logout_admin, name="logout_admin"),
    path("panel/reportes/", views.admin_reportes, name="admin_reportes"),
    path("panel/editar/<int:id>/", views.editar_reporte, name="editar_reporte"),
    path("panel/cambiar-estado/<int:id>/", views.cambiar_estado_reporte, name="cambiar_estado_reporte"),
    path("admin/", admin.site.urls),
    path("panel/", views.panel_personalizado, name="panel_personalizado"),

    path('panel/alertas/', views.gestionar_alertas, name='gestionar_alertas'),
    path('panel/alertas/crear/', views.crear_alerta, name='crear_alerta'),
    path('panel/alertas/editar/<int:alerta_id>/', views.editar_alerta, name='editar_alerta'),
    path('panel/alertas/eliminar/<int:alerta_id>/', views.eliminar_alerta, name='eliminar_alerta'),
]

