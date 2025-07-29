# Seguir en el shell donde ya estás
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth.models import User

from app.admin_custom.models import Alerta, HistorialNotificacion

print("🔄 Migrando alertas existentes...")

for alerta in Alerta.objects.all():
    print(f"\n📋 Procesando: {alerta.titulo}")
    
    # Verificar si ya tiene historial
    if HistorialNotificacion.objects.filter(alerta=alerta).exists():
        print("Ya tiene historial, saltando...")
        continue
    
    # Crear registros de historial
    if alerta.enviar_a_todos:
        # Si es para todos
        HistorialNotificacion.objects.create(
            alerta=alerta,
            usuario_destinatario=None,
            zona=alerta.ubicacion or "General",
            estado_entrega='enviado',
            tipo_notificacion='sistema'
        )
        print("Registrado para TODOS los usuarios")
    else:
        # Si es para destinatarios específicos
        destinatarios = alerta.destinatarios.all()
        if destinatarios.exists():
            for destinatario in destinatarios:
                HistorialNotificacion.objects.create(
                    alerta=alerta,
                    usuario_destinatario=destinatario,
                    zona=alerta.ubicacion or "General",
                    estado_entrega='enviado',
                    tipo_notificacion='sistema'
                )
            print(f"   ✅ Registrado para {destinatarios.count()} usuarios específicos")
        else:
            # Sin destinatarios específicos, asumir general
            HistorialNotificacion.objects.create(
                alerta=alerta,
                usuario_destinatario=None,
                zona=alerta.ubicacion or "General",
                estado_entrega='enviado',
                tipo_notificacion='sistema'
            )
            print("Sin destinatarios específicos, registrado como general")

print("¡Migración completada!")
print(f"📊 Registros en historial: {HistorialNotificacion.objects.count()}")