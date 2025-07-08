from django.urls import path
from . import views_alertas

app_name = 'traffic'

urlpatterns = [
    # URLs originales
    path('create/', views.create_report, name='create_report'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Nuevas APIs para alertas y notificaciones
    path('api/alertas/crear/', views_alertas.crear_alerta, name='crear_alerta'),
    path('api/usuarios/ubicacion/', views_alertas.procesar_ubicacion_usuario, name='procesar_ubicacion'),
    path('api/usuarios/configurar-notificaciones/', views_alertas.configurar_notificaciones_usuario, name='configurar_notificaciones'),
    path('api/usuarios/<int:usuario_id>/notificaciones/', views_alertas.obtener_notificaciones_usuario, name='obtener_notificaciones'),
]
