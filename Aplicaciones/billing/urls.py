from django.urls import path
from . import views

app_name = "billing"
urlpatterns = [
    path('seleccionar-cliente/', views.seleccionar_cliente, name='seleccionar_cliente'),
    path('anadir-item-inventario/<str:id_producto>/', views.anadirItemInventario, name='añadir_item_inventario'),
    path('mostrar-carrito/', views.mostrar_carrito, name='mostrar_carrito'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
    path('listar-facturas/', views.listar_facturas, name='listar_facturas'),
    path('generar-pdf/<str:id_factura>/', views.generar_pdf_factura, name='generar_pdf_factura'),
    ]
