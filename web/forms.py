# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ReporteColaborativo, Alerta

FORM_CONTROL = 'form-control'
FORM_CONTROL_PASSWORD_INPUT = 'form-control password-input'

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

# Nuevo formulario de login
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': FORM_CONTROL,
        'placeholder': 'Usuario o correo electrónico',
        'id': 'username',
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': FORM_CONTROL_PASSWORD_INPUT,
        'placeholder': 'Contraseña',
        'id': 'password',
    }))

class ReporteColaborativoForm(forms.ModelForm):
    class Meta:
        model = ReporteColaborativo
        exclude = ['usuario_reportador', 'fecha_creacion', 'fecha_actualizacion', 'votos_positivos', 'votos_negativos', 'usuarios_votantes', 'es_validado', 'estado_reporte']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del incidente'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describa lo sucedido'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Venezuela, Cercado'}),
            'tipo_incidente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Robo, incendio...'}),
            'imagen_geolocalizada': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'nivel_peligro': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }

class AlertaForm(forms.ModelForm):
    destinatarios = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'id': 'destinatarios',
        }),
        required=False,
    )

    class Meta:
        model = Alerta
        fields = ['titulo', 'mensaje', 'destinatarios', 'ubicacion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': FORM_CONTROL}),
            'mensaje': forms.Textarea(attrs={'class': FORM_CONTROL}),
            'ubicacion': forms.TextInput(attrs={'class': FORM_CONTROL}),
        }
