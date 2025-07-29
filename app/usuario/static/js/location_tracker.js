// app/usuario/static/js/location_tracker.js
// Sistema de tracking de ubicación y notificaciones en tiempo real

class LocationTracker {
    constructor() {
        this.userLocation = null;
        this.notificationConfig = null;
        this.locationUpdateInterval = null;
        this.notificationsActive = false;
        this.watchId = null;
        this.lastNotificationTime = {};
        
        this.init();
    }

    async init() {
        console.log('🚦 Inicializando sistema de notificaciones de tráfico...');
        
        // Verificar soporte de geolocalización
        if (!navigator.geolocation) {
            this.showLocationStatus('❌ Geolocalización no soportada', 'error');
            return;
        }
        
        // Cargar configuración
        await this.loadNotificationSettings();
        
        // Iniciar tracking de ubicación
        this.startLocationTracking();
        
        console.log('✅ Sistema de notificaciones inicializado');
    }

    async loadNotificationSettings() {
        try {
            const response = await fetch('/api/notificaciones/config/');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.notificationConfig = data.config;
                this.notificationsActive = data.config.notificaciones_activas;
                console.log('📱 Configuración cargada:', this.notificationConfig);
                
                this.updateNotificationUI();
            }
        } catch (error) {
            console.error('❌ Error cargando configuración:', error);
        }
    }

    startLocationTracking() {
        if (!this.notificationsActive) {
            console.log('🔕 Notificaciones desactivadas');
            return;
        }

        // Obtener ubicación inicial
        this.getCurrentLocation();
        
        // Configurar tracking continuo con watchPosition
        if (navigator.geolocation) {
            this.watchId = navigator.geolocation.watchPosition(
                (position) => this.handleLocationUpdate(position),
                (error) => this.handleLocationError(error),
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 30000
                }
            );
        }

        // Configurar actualización periódica adicional
        const frequency = (this.notificationConfig?.frecuencia_actualizacion || 30) * 1000;
        
        if (this.locationUpdateInterval) {
            clearInterval(this.locationUpdateInterval);
        }
        
        this.locationUpdateInterval = setInterval(() => {
            if (this.notificationsActive && this.userLocation) {
                this.sendLocationUpdate(this.userLocation.lat, this.userLocation.lng);
            }
        }, frequency);

        console.log(`⏱️ Tracking iniciado con frecuencia: ${frequency/1000}s`);
    }

    stopLocationTracking() {
        if (this.watchId) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
        
        if (this.locationUpdateInterval) {
            clearInterval(this.locationUpdateInterval);
            this.locationUpdateInterval = null;
        }

        console.log('🛑 Tracking de ubicación detenido');
    }

    getCurrentLocation() {
        this.showLocationStatus('📍 Obteniendo ubicación...', 'info');
        
        navigator.geolocation.getCurrentPosition(
            (position) => this.handleLocationUpdate(position),
            (error) => this.handleLocationError(error),
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    }

    handleLocationUpdate(position) {
        this.userLocation = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date()
        };
        
        // Enviar ubicación al servidor
        this.sendLocationUpdate(this.userLocation.lat, this.userLocation.lng);
        
        this.showLocationStatus('✅ Ubicación actualizada', 'success');
        
        console.log(`📍 Ubicación actualizada: ${this.userLocation.lat}, ${this.userLocation.lng} (±${this.userLocation.accuracy}m)`);
    }

    handleLocationError(error) {
        let message = 'Error obteniendo ubicación';
        
        switch(error.code) {
            case error.PERMISSION_DENIED:
                message = '❌ Permisos de ubicación denegados';
                break;
            case error.POSITION_UNAVAILABLE:
                message = '❌ Ubicación no disponible';
                break;
            case error.TIMEOUT:
                message = '⏱️ Tiempo agotado obteniendo ubicación';
                break;
        }
        
        console.error('❌ Error de geolocalización:', error);
        this.showLocationStatus(message, 'error');
    }

    async sendLocationUpdate(lat, lng) {
        try {
            const response = await fetch('/api/ubicacion/actualizar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    latitud: lat,
                    longitud: lng
                })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                // Procesar notificaciones si las hay
                if (data.notifications && data.notifications.length > 0) {
                    this.processTrafficNotifications(data.notifications);
                }
                
                this.updateNotificationBadge(data.notifications?.length || 0);
                this.updateTrafficStatus();
            } else {
                console.error('❌ Error del servidor:', data.message);
            }
        } catch (error) {
            console.error('❌ Error enviando ubicación:', error);
        }
    }

    async updateTrafficStatus() {
        if (!this.userLocation) return;
        
        try {
            const response = await fetch('/api/notificaciones/estadisticas/');
            const data = await response.json();
            
            if (data.status === 'success') {
                const stats = data.stats;
                this.updateTrafficUI(stats);
            }
        } catch (error) {
            console.error('❌ Error obteniendo estadísticas:', error);
        }
    }

    updateTrafficUI(stats) {
        // Actualizar contadores
        const elements = {
            'reportes-count': stats.reportes_cercanos,
            'radio-config': stats.radio_configurado + ' km'
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        });

        // Actualizar timestamp
        if (stats.ultima_actualizacion) {
            const fecha = new Date(stats.ultima_actualizacion);
            const element = document.getElementById('last-update');
            if (element) element.textContent = fecha.toLocaleTimeString();
        }

        // Actualizar estado visual
        this.updateTrafficStatusVisual(stats.reportes_cercanos);
    }

    updateTrafficStatusVisual(reportesCercanos) {
        const statusElement = document.getElementById('traffic-status');
        const messageElement = document.getElementById('traffic-message');
        
        if (!statusElement || !messageElement) return;

        if (reportesCercanos === 0) {
            statusElement.className = 'traffic-status status-good';
            messageElement.innerHTML = '<i class="bi bi-check-circle me-2"></i>Tráfico fluido en tu zona';
        } else if (reportesCercanos <= 2) {
            statusElement.className = 'traffic-status status-warning';
            messageElement.innerHTML = `<i class="bi bi-exclamation-triangle me-2"></i>Atención: ${reportesCercanos} incidente(s) cercano(s)`;
        } else {
            statusElement.className = 'traffic-status status-danger pulse-animation';
            messageElement.innerHTML = `<i class="bi bi-exclamation-octagon me-2"></i>Congestión alta: ${reportesCercanos} incidentes`;
        }
    }

    processTrafficNotifications(notifications) {
        notifications.forEach(notification => {
            // Evitar spam de notificaciones del mismo incidente
            const key = `${notification.id}_${notification.tipo}`;
            const now = Date.now();
            
            if (this.lastNotificationTime[key] && (now - this.lastNotificationTime[key]) < 300000) {
                return; // No mostrar si ya se mostró en los últimos 5 minutos
            }
            
            this.lastNotificationTime[key] = now;
            this.showTrafficNotification(notification);
        });
    }

    showTrafficNotification(notification) {
        // Crear elemento de notificación
        const toast = document.createElement('div');
        toast.className = 'toast show';
        toast.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999; min-width: 320px; max-width: 400px;';
        
        const nivelColor = {
            1: 'success',
            2: 'warning', 
            3: 'danger',
            4: 'danger'
        }[notification.nivel_peligro] || 'info';
        
        const nivelTexto = {
            1: 'Bajo',
            2: 'Medio',
            3: 'Alto',
            4: 'Crítico'
        }[notification.nivel_peligro] || 'Medio';
        
        toast.innerHTML = `
            <div class="toast-header bg-${nivelColor} text-white">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                <strong class="me-auto">Alerta de Tráfico</strong>
                <small class="text-white-50">${notification.distancia.toFixed(1)}km</small>
                <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
            <div class="toast-body">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <strong class="text-dark">${notification.titulo}</strong>
                    <span class="badge bg-${nivelColor}">${nivelTexto}</span>
                </div>
                <div class="text-muted mb-2">
                    <i class="bi bi-geo-alt me-1"></i>${notification.ubicacion}
                </div>
                <div class="text-dark">
                    ${notification.mensaje}
                </div>
                <div class="mt-2 d-flex justify-content-between">
                    <small class="text-muted">
                        <i class="bi bi-clock me-1"></i>Ahora
                    </small>
                    <button class="btn btn-outline-primary btn-sm" onclick="this.closest('.toast').remove()">
                        <i class="bi bi-check-lg me-1"></i>OK
                    </button>
                </div>
            </div>
        `;
        
        // Agregar al DOM
        document.body.appendChild(toast);
        
        // Auto-remove después de 10 segundos
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 10000);
        
        // Reproducir sonido de notificación
        this.playNotificationSound();
        
        // Vibración en dispositivos móviles
        if ('vibrate' in navigator) {
            navigator.vibrate([200, 100, 200]);
        }

        console.log(`🚨 Notificación mostrada: ${notification.titulo} (${notification.distancia.toFixed(1)}km)`);
    }

    playNotificationSound() {
        try {
            // Crear un sonido sutil para las notificaciones
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.3);
        } catch (error) {
            console.log('🔇 No se pudo reproducir sonido de notificación');
        }
    }

    // Métodos públicos para controlar el sistema
    toggleNotifications() {
        this.notificationsActive = !this.notificationsActive;
        
        if (this.notificationsActive) {
            this.startLocationTracking();
            this.updateNotificationIcon('bi-bell-fill');
            console.log('🔔 Notificaciones activadas');
        } else {
            this.stopLocationTracking();
            this.updateNotificationIcon('bi-bell-slash');
            console.log('🔕 Notificaciones desactivadas');
        }
        
        // Actualizar configuración en el servidor
        this.updateServerConfig({ notificaciones_activas: this.notificationsActive });
    }

    async updateServerConfig(config) {
        try {
            const response = await fetch('/api/notificaciones/config/actualizar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify(config)
            });

            const data = await response.json();
            if (data.status === 'success') {
                Object.assign(this.notificationConfig, config);
                console.log('⚙️ Configuración actualizada en servidor');
            }
        } catch (error) {
            console.error('❌ Error actualizando configuración:', error);
        }
    }

    forceLocationUpdate() {
        console.log('🔄 Forzando actualización de ubicación...');
        this.getCurrentLocation();
    }

    // Métodos auxiliares para UI
    updateNotificationIcon(iconClass) {
        const icon = document.getElementById('notification-icon');
        if (icon) {
            icon.className = iconClass;
        }
    }

    updateNotificationBadge(count) {
        const badge = document.getElementById('notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    updateNotificationUI() {
        const icon = document.getElementById('notification-icon');
        if (icon) {
            icon.className = this.notificationsActive ? 'bi bi-bell-fill' : 'bi bi-bell-slash';
        }
    }

    showLocationStatus(message, type) {
        const statusElement = document.getElementById('location-text');
        if (statusElement) {
            statusElement.textContent = message;
        }

        // También mostrar en consola con emoji apropiado
        const emoji = {
            'info': 'ℹ️',
            'success': '✅',
            'error': '❌'
        }[type] || 'ℹ️';
        
        console.log(`${emoji} ${message}`);
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Método para limpiar recursos
    destroy() {
        this.stopLocationTracking();
        this.userLocation = null;
        this.notificationConfig = null;
        console.log('🧹 LocationTracker destruido');
    }
}

// Funciones globales para compatibilidad con el HTML existente
let locationTracker = null;

function initializeTrafficNotifications() {
    if (!locationTracker) {
        locationTracker = new LocationTracker();
    }
}

function updateLocation() {
    if (locationTracker) {
        locationTracker.forceLocationUpdate();
    }
}

function toggleNotifications() {
    if (locationTracker) {
        locationTracker.toggleNotifications();
    }
}

// Auto-inicializar cuando se carga el DOM
document.addEventListener('DOMContentLoaded', function() {
    initializeTrafficNotifications();
});

// Limpiar recursos cuando se cierra la página
window.addEventListener('beforeunload', function() {
    if (locationTracker) {
        locationTracker.destroy();
    }
});