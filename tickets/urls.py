from django.urls import path
from . import views

urlpatterns = [
    path('', views.crear_queja, name='crear_queja'),
    path('exito/', views.pagina_exito, name='pagina_exito'),
    path('transparencia/', views.dashboard_publico, name='dashboard_publico'),
]