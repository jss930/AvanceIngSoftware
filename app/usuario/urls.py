from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.RegistroUsuarioView.as_view(), name='register'),
    
    path('login/', views.LoginView.as_view(), name='login'),  
    path('logout/', views.logout_view, name='logout'),  
    
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),  # Nueva ruta

]