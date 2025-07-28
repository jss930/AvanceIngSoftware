# Laboratorio 11: Clean Code

## Autor
**David A. Espinoza B.**  
**Módulo:** Panel Administrativo (Control de Reportes)

## Herramientas y Tecnologías
- Python 3.12.3
- Django 5.2.3
- SonarLint (Análisis estático)
- Git (Control de versiones)

## Problemas Detectados y Corregidos

### Bugs Críticos
| Problema | Archivo | Corrección | Impacto |
|----------|---------|------------|---------|
| Acceso inseguro a POST | `views.py` | Reemplazado por `.get()` con sanitización | Previene KeyError y XSS básico |
| Filtrado case-sensitive | `views.py` | Búsqueda case-insensitive | Mejora experiencia de usuario |

### Code Smells
| Problema | Archivo | Corrección | Impacto |
|----------|---------|------------|---------|
| Código duplicado en validaciones | `views.py` | Extraído a función `sanitizar_input()` | Reduce duplicación |
| Lógica de login mezclada | `views.py` | Separada en helpers | Más fácil de testear |

### Vulnerabilidades
| Problema | Archivo | Corrección | Impacto |
|----------|---------|------------|---------|
| Falta de logging | `views.py` | Agregado sistema de logging | Permite auditoría |
| Caching en vistas admin | `views.py` | Agregado `@never_cache` | Previene datos sensibles en cache |

## Mejoras Implementadas

### Seguridad Reforzada
```python
# Decorador personalizado para admin
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            logger.warning(f"Intento de acceso no autorizado: {request.user}")
            return redirect('custom_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
```

### Documentación Mejorada
```python
def custom_login(request):
    """
    Maneja autenticación segura para administradores con:
    - Validación de campos obligatorios
    - Sanitización de inputs
    - Protección CSRF
    - Logging de actividades
    """
    ...
```

### Logging de Actividades
```python
try:
    # Operación crítica
except Exception as e:
    logger.error(f"Error en admin_reportes: {str(e)}")
    messages.error(request, "Error al procesar la solicitud")
```

**Nota:** El módulo `editar_reporte` se mantuvo en su versión anterior por requisitos del laboratorio, pero contiene las mejoras básicas de seguridad.