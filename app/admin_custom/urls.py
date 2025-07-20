# urls.py
from django.urls import path
from .views import admin_reportes, logout_admin, custom_login, panel_personalizado
from django.contrib import admin

urlpatterns = [
    path('loginadmin/', custom_login, name='custom_login'),  # Login para admin
    path('logout_admin/', logout_admin, name='logout_admin'),  #logout admin
    path('panel/reportes/', admin_reportes, name='admin_reportes'),  #control reportes
    path('admin/', admin.site.urls),
    path('panel/', panel_personalizado, name='panel_personalizado'),
]
