from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inventario/carrito/', include('Aplicaciones.billing.urls')),
    path('inventario/', include('Aplicaciones.inventory.urls')),
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
