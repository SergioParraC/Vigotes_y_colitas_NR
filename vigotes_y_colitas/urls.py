"""
URL configuration for vigotes_y_colitas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inventario/', include('Aplicaciones.inventory.urls')),
    # Sin esta ruta, abrir http://127.0.0.1:8000/ (la URL que imprime runserver)
    # devuelve 404 y parece que la aplicación no funcionara: el catálogo vive
    # en /inventario/. Aquí sólo se redirige para que la raíz nunca dé 404.
    path(
        '',
        RedirectView.as_view(
            pattern_name='inventario:productos_cliente', permanent=False
        ),
        name='inicio',
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
