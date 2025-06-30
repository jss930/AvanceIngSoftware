from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Correo electrónico',
        'id': 'email',
    }))
    
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Usuario',
        'id': 'username',
    }))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control password-input',
        'placeholder': 'Contraseña',
        'id': 'password1',
    }))
    
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control password-input',
        'placeholder': 'Confirmar contraseña',
        'id': 'password2',
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
