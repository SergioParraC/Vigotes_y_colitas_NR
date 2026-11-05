from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
    # Categorías
    path('categoria/', views.home_categorias, name='listado_categorias'),
    path('categoria/crear/', views.crear_categoria_formulario, name='crear_categoria'),
    path('categoria/<str:id_categoria>/', views.guardar_categoria, name='guardar_categoria'),

    # Proveedores
    path('proveedor/', views.home_proveedores, name='listado_proveedores'),
    path('proveedor/crear/', views.crear_proveedor_formulario, name='crear_proveedor'),
    path('proveedor/pdf/', views.generar_pdf_proveedores, name='pdf_proveedores'),
    path('proveedor/eliminar/<str:id_proveedor>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('proveedor/<str:id_proveedor>/', views.guardar_proveedor, name='guardar_proveedor'),
    
    # Productos
    path('listado-productos/', views.home_producto, name='listado_productos'),
    path('crear/', views.crear_producto_formulario, name='crear_producto_formulario'),
    path('filtrar/', views.filtrar_productos, name='filtrar_productos'),
    path('productos/pdf/', views.generar_pdf_productos, name='pdf_productos'),
    path('eliminado/<str:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
    path('detalle/<str:id_producto>/', views.detalle_producto_cliente, name='detalle_producto_cliente'),
    path('', views.productos_cliente, name='productos_cliente'),
    path('<str:id_producto>/', views.guardar_producto, name='guardar_producto'),
]
