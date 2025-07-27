# app/usuario/admin.py - AGREGAR esto al archivo existente

from django.contrib import admin
from .models import PerfilUsuario

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 
        'notificaciones_activas', 
        'radio_notificacion', 
        'total_notificaciones_recibidas',
        'ultima_actualizacion_ubicacion'
    ]
    
    list_filter = [
        'notificaciones_activas',
        'fecha_creacion',
        'ultima_actualizacion_ubicacion'
    ]
    
    search_fields = ['usuario__username', 'usuario__email']
    
    readonly_fields = [
        'fecha_creacion', 
        'fecha_actualizacion', 
        'total_notificaciones_recibidas',
        'ultima_actualizacion_ubicacion'
    ]
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Configuración de Notificaciones', {
            'fields': (
                'notificaciones_activas',
                'radio_notificacion',
                'frecuencia_actualizacion',
                'tipos_incidentes_notificar'
            )
        }),
        ('Ubicación Actual', {
            'fields': (
                'latitud_actual',
                'longitud_actual',
                'ultima_actualizacion_ubicacion'
            ),
            'classes': ['collapse']
        }),
        ('Estadísticas', {
            'fields': (
                'total_notificaciones_recibidas',
                'fecha_creacion',
                'fecha_actualizacion'
            ),
            'classes': ['collapse']
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')