# app/usuario/tests.py - AGREGAR estos tests

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
import json
from .models import PerfilUsuario
from app.reporte.models import ReporteColaborativo
from app.servicios.notificationApplicationService import NotificationApplicationService

class NotificationSystemTests(TestCase):
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.perfil = PerfilUsuario.get_or_create_for_user(self.user)
        
        # Crear reporte de prueba
        self.reporte = ReporteColaborativo.objects.create(
            titulo='Embotellamiento de prueba',
            descripcion='Embotellamiento en av. test',
            tipo_incidente='embotellamiento',
            latitud=Decimal('-16.4090'),
            longitud=Decimal('-71.5375'),
            usuario_reportador=self.user,
            nivel_peligro=2,
            is_active=True
        )

    def test_crear_perfil_automatico(self):
        """Test que se crea automáticamente un perfil al crear usuario"""
        nuevo_user = User.objects.create_user(
            username='newuser',
            password='pass123'
        )
        self.assertTrue(hasattr(nuevo_user, 'perfil'))
        self.assertTrue(nuevo_user.perfil.notificaciones_activas)

    def test_api_actualizar_ubicacion(self):
        """Test de la API para actualizar ubicación"""
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'latitud': -16.4090,
            'longitud': -71.5375
        }
        
        response = self.client.post(
            reverse('actualizar_ubicacion'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')

    def test_api_configuracion_notificaciones(self):
        """Test de la API para obtener configuración"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('obtener_configuracion_notificaciones'))
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('config', response_data)

    def test_notificacion_service_ubicacion(self):
        """Test del servicio de notificaciones"""
        service = NotificationApplicationService()
        
        resultado = service.actualizar_ubicacion_usuario(
            usuario_id=self.user.id,
            latitud=-16.4090,
            longitud=-71.5375
        )
        
        self.assertEqual(resultado['status'], 'success')
        
        # Verificar que se actualizó la ubicación
        self.perfil.refresh_from_db()
        self.assertEqual(float(self.perfil.latitud_actual), -16.4090)
        self.assertEqual(float(self.perfil.longitud_actual), -71.5375)

    def test_deteccion_zonas_congestionadas(self):
        """Test de detección de zonas congestionadas"""
        service = NotificationApplicationService()
        
        # Ubicar al usuario cerca del reporte
        resultado = service.verificar_zonas_congestionadas_cercanas(
            user=self.user,
            latitud=-16.4090,  # Misma ubicación que el reporte
            longitud=-71.5375
        )
        
        self.assertEqual(resultado['status'], 'success')
        self.assertGreater(len(resultado['notifications']), 0)

    def test_configuracion_tipos_incidentes(self):
        """Test de configuración de tipos de incidentes"""
        service = NotificationApplicationService()
        
        nueva_config = {
            'tipos_incidentes_notificar': ['accidente', 'construccion']
        }
        
        resultado = service.actualizar_configuracion_notificaciones(
            usuario_id=self.user.id,
            config=nueva_config
        )
        
        self.assertEqual(resultado['status'], 'success')
        
        # Verificar que se actualizó
        self.perfil.refresh_from_db()
        self.assertEqual(
            set(self.perfil.tipos_incidentes_notificar),
            {'accidente', 'construccion'}
        )

    def test_radio_notificacion(self):
        """Test del radio de notificación"""
        # Configurar radio pequeño
        self.perfil.radio_notificacion = 0.5
        self.perfil.save()
        
        service = NotificationApplicationService()
        
        # Ubicar al usuario lejos del reporte (más de 0.5km)
        resultado = service.verificar_zonas_congestionadas_cercanas(
            user=self.user,
            latitud=-16.4000,  # ~1km del reporte
            longitud=-71.5300
        )
        
        # No debería recibir notificaciones
        self.assertEqual(len(resultado['notifications']), 0)

class PerfilUsuarioModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_get_or_create_perfil(self):
        """Test del método get_or_create_for_user"""
        perfil = PerfilUsuario.get_or_create_for_user(self.user)
        
        self.assertIsNotNone(perfil)
        self.assertTrue(perfil.notificaciones_activas)
        self.assertEqual(perfil.radio_notificacion, 2.0)

    def test_ubicacion_reciente(self):
        """Test del método tiene_ubicacion_reciente"""
        perfil = PerfilUsuario.get_or_create_for_user(self.user)
        
        # Sin ubicación
        self.assertFalse(perfil.tiene_ubicacion_reciente())
        
        # Con ubicación actual
        from django.utils import timezone
        perfil.ultima_actualizacion_ubicacion = timezone.now()
        perfil.save()
        
        self.assertTrue(perfil.tiene_ubicacion_reciente())

# Ejecutar tests con:
# python manage.py test app.usuario.tests