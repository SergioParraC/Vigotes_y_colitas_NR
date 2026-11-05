from django.urls import path
from . import views

app_name = "citas"

urlpatterns = [
    path('', views.home_citas, name='listado_citas'),
    path('crear/', views.crear_cita, name='crear_cita'),
    path('buscar/', views.buscar_cita, name='buscar_cita'),
    path('filtrar/', views.filtrar_citas, name='filtrar_citas'),
    path('eliminar/<str:id_cita>/', views.eliminar_cita, name='eliminar_cita'),
    path('eliminado/<str:id_cita>/', views.eliminar_cita),
    path('<str:id_cita>/', views.detalle_cita, name='detalle_cita'),
]
