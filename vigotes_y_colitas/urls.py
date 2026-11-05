from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # La página principal (home y contacto) vive en el aplicativo customers
    path('', include('Aplicaciones.customers.urls')),
    path('inventario/carrito/', include('Aplicaciones.billing.urls')),
    path('inventario/', include('Aplicaciones.inventory.urls')),
    path('pets/', include('Aplicaciones.pets.urls')),
    path('citas/', include('Aplicaciones.meeting.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
