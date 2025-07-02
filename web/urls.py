# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.RegistroUsuarioView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),  # Cambiado de views.home
    path('logout/', views.logout_view, name='logout'),  # Nueva ruta
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),  # Nueva ruta
    path('test/', views.test, name='test'),  # Tu vista de prueba existente
]