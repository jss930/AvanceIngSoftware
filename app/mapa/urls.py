# urls.py
from django.urls import path
from . import views
urlpatterns = [
    path('plan_route/', views.PlanRouteView.as_view(), name='plan_route'),
    path('see_state/', views.SeeStateView.as_view(), name='see_state'),
]