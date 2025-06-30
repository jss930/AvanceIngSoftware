from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('register/', views.register, name='register'),
    path('register/', views.RegistroUsuarioView.as_view(), name='register'),
    #! modificar view de login
    path('login/', views.home, name='login'),
    #! agregar vista test, para validar creación de cuenta
    path('test/', views.test, name='test'),

]
    