from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_directo'),
    path('contacto/', views.contacto, name='contacto'),
]
