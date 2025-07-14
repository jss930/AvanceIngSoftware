# 📢 LABORATORIO 10/Cesar Carpio

##  Objetivo
Aplicar estilos de programación consistentes en los módulos asignados como parte del proyecto final del curso.

---

## ✅ Estilos de Programación Aplicados

1. **Lazy Rivers**  
   Flujo claro: `initForm()` → setup de eventos → validaciones → envío.
   
   (templates/report_incident.html) 63-111
   ```javascript
   // [Pipeline] Flujo de inicialización
   $(document).ready(function initForm() {
    setupDescriptionValidation();        // [Pipeline] fase 1
    setupPhotoValidation();              // [Pipeline] fase 2
    setupFormSubmission();               // [Pipeline] fase 3
   });

2. **Pipeline**  
   secuencia bien estructurada de rutas que componen el flujo de navegación y acceso a funcionalidades del sistema.

   (web/urls.py)
   ```python
   # [Pipeline] Flujo de URLs que estructuran el sistema
   urlpatterns = [
    path('', views.home, name='home'),                              # Página de inicio
    path('register/', views.RegistroUsuarioView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),              # Login de usuario
    path('loginadmin/', custom_login, name='custom_login'),         # Login de administrador
    path('logout/', views.logout_view, name='logout'),
    path('logout_admin/', views.logout_admin, name='logout_admin'),
    path('panel/reportes/', admin_reportes, name='admin_reportes'), # Panel de administración
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('plan_route/', views.PlanRouteView.as_view(), name='plan_route'),
    path('report_incident/', views.ReportIncidentView.as_view(), name='report_incident'),
    path('see_state/', views.SeeStateView.as_view(), name='see_state'),
    path('reportes/', views.lista_reportes, name='lista_reportes'),
    path('reportes/agregar/', views.agregar_reporte, name='agregar_reporte'),
    path('reportes/eliminar/<int:id>/', views.eliminar_reporte, name='eliminar_reporte'),
   ]

3. **Error / Exception Handling**  
   - Reemplazo de `alert()` por mensajes inline.  

   (web/models.py)  
   ```python
   class ReporteColaborativo(models.Model):
       # ... campos ...
    def clean(self):
        if self.estado_reporte not in ['pendiente', 'probado', 'rechazado']:
            raise ValidationError({'estado_reporte': 'Valor no válido para el estado del reporte.'})
        # Validaciones adicionales

4. **Things**  
   clases RegistroUsuarioForm, LoginForm y ReporteColaborativoForm representan entidades independientes, cada una con su propio conjunto de campos, validaciones y comportamiento de presentación. Son “cosas” autocontenidas y reutilizables:  
   ```python
   class RegistroUsuarioForm(UserCreationForm):
       email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
           'class': FORM_CONTROL,
           'placeholder': 'Correo electrónico',
           'id': 'email',
       }))
   
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': FORM_CONTROL,
        'placeholder': 'Usuario',
        'id': 'username',
    }))
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': FORM_CONTROL_PASSWORD_INPUT,
        'placeholder': 'Contraseña',
        'id': 'password1',
    }))
   
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': FORM_CONTROL_PASSWORD_INPUT,
        'placeholder': 'Confirmar contraseña',
        'id': 'password2',
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

5. **Trinity (Separación MVC mínima)**  
   - **Modelo**: lectura de datos del formulario.  
   - **Vista**: funciones 
   - **Controlador**

   ```python
   my_project/
   ├── manage.py
   ├── README.md
   ├── requirements.txt
   ├── .env
   ├── web/            # Carpeta del proyecto (configuración)
   │   ├── __init__.py
   │   ├── settings.py        
   │   ├── urls.py            # Controlador principal (URL dispatcher)
   │   ├── wsgi.py
   │   └── asgi.py
   ├── apps/                  
   │   └── reporte/           
   │       ├── __init__.py
   │       ├── admin.py
   │       ├── apps.py
   │       ├── models.py      # Modelo (Modelo)
   │       ├── forms.py       
   │       ├── views.py       # Lógica y respuestas HTTP (Controlador)
   │       ├── urls.py        
   │       ├── templates/     # Templates HTML (Vista)
   │       │   └── reporte/
   │       ├── static/        
   │       └── migrations/
   └── templates/             # Templates globales (Vista)
       ├── base.html
       └── ...

---


