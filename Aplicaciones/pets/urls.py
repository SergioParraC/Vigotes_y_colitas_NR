from django.urls import path
from . import views

app_name = "pets"

urlpatterns = [
    path('', views.home_pets, name='listado_mascotas'),
    path('mascotas/crear/', views.registrar_mascota, name='crear_mascota'),
    path('mascotas/<str:id_mascota>/historia/', views.historia_mascota, name='historia_mascota'),
    path('mascotas/<str:id_mascota>/editar/', views.editar_mascota, name='editar_mascota'),
    path('vacunas/crear/', views.registrar_vacuna, name='crear_vacuna'),
    path('vacunas/<str:id_vacuna>/editar/', views.editar_vacuna, name='editar_vacuna'),
    path('historiales/crear/', views.registrar_historial, name='crear_historial'),
    path('historiales/<str:id_historial>/editar/', views.editar_historial, name='editar_historial'),
]
