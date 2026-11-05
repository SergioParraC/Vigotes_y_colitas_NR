from datetime import date

from bson.objectid import ObjectId
from django.test import TransactionTestCase
from django.urls import reverse

from ..customers import models as customers
from ..inventory import models as inventory
from . import models


class BillingTestCase(TransactionTestCase):
    """Pruebas del carrito y de la facturación (djongo no soporta transacciones)."""

    def setUp(self):
        self.categoria = inventory.Categoria(
            nombre='Medicamentos', descripcion='Uso veterinario')
        self.categoria.save()
        self.proveedor = inventory.Proveedor(
            nombre='Distribuidora SAS', contacto='Ana Perez',
            telefono='3001234567', email='ventas@distribuidora.com',
            direccion='Calle 10 # 20-30')
        self.proveedor.save()
        self.producto = self._crear_producto('Vitamina B12', 25000, 10)
        self.cliente = self._crear_cliente()

    def _crear_producto(self, nombre, precio, stock):
        producto = inventory.Productos(
            nombre=nombre,
            categoria={
                '_id': self.categoria.pk,
                'nombre': self.categoria.nombre,
                'descripcion': self.categoria.descripcion,
            },
            proveedor={
                '_id': self.proveedor.pk,
                'nombre': self.proveedor.nombre,
                'contacto': self.proveedor.contacto,
                'telefono': self.proveedor.telefono,
                'email': self.proveedor.email,
                'direccion': self.proveedor.direccion,
            },
            descripcion='Suplemento vitamínico',
            precio=precio,
            stock=stock,
        )
        producto.save()
        return producto

    def _crear_cliente(self):
        cliente = customers.Cliente(
            mascotas=[],
            nombre='Ana',
            apellido='Perez',
            numero_documeto='10203040',
            email='ana@correo.com',
            telefono='3001234567',
            direccion='Calle 1 # 2-3',
        )
        cliente.save()
        return cliente

    def _crear_mascota(self):
        self.cliente.mascotas = [{
            '_id': ObjectId(),
            'historia_clinica': [],
            'vacunas': [],
            'citas': [],
            'nombre': 'Firulais',
            'especie': 'Perro',
            'raza': 'Criollo',
            'fecha_nacimiento': date(2020, 1, 1),
            'peso': 10.5,
            'vacunado': True,
        }]
        self.cliente.save()
        return self.cliente.mascotas[0]

    def _url_anadir(self, producto=None):
        producto = producto or self.producto
        return reverse('billing:añadir_item_inventario', args=[producto.pk])

    def _sesion_con_producto(self, cantidad=2):
        session = self.client.session
        session['id_producto'] = str(self.producto.pk)
        session['cantidad'] = cantidad
        session.save()

    def _elegir_cliente(self):
        return self.client.post(
            reverse('billing:seleccionar_cliente'),
            {'cliente': str(self.cliente.pk)},
        )

    def _factura_borrador_con(self, cantidad=2, mascota=''):
        self._sesion_con_producto(cantidad)
        self._elegir_cliente()
        self.client.post(
            reverse('billing:seleccionar_mascota'),
            {'mascota': mascota},
            follow=True,
        )

    # Carrito --------------------------------------------------------------
    def test_anadir_al_carrito_sin_factura_pide_el_cliente(self):
        response = self.client.post(self._url_anadir(), {'cantidad': 2})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], reverse('billing:seleccionar_cliente'))
        self.assertEqual(
            self.client.session['id_producto'], str(self.producto.pk))
        self.assertEqual(self.client.session['cantidad'], 2)
        self.assertFalse(models.Facturas.objects.exists())

    def test_seleccionar_cliente_pide_la_mascota(self):
        self._sesion_con_producto(cantidad=3)
        response = self._elegir_cliente()
        self.assertRedirects(
            response, reverse('billing:seleccionar_mascota'))
        self.assertEqual(
            self.client.session['cliente_id'], str(self.cliente.pk))
        self.assertFalse(models.Facturas.objects.exists())

    def test_seleccionar_mascota_crea_la_factura_en_borrador(self):
        self._sesion_con_producto(cantidad=3)
        self._elegir_cliente()
        response = self.client.post(
            reverse('billing:seleccionar_mascota'),
            {'mascota': ''},
            follow=True,
        )
        self.assertContains(response, 'Vitamina B12')
        factura = models.Facturas.objects.get(estado='BORRADOR')
        self.assertEqual(factura.cliente['nombre'], 'Ana')
        self.assertFalse(factura.mascota)
        self.assertEqual(len(factura.factura_detalle), 1)
        self.assertEqual(factura.factura_detalle[0]['cantidad'], 3)
        self.assertEqual(factura.factura_detalle[0]['subtotal'], 75000)
        producto = inventory.Productos.objects.get(pk=self.producto.pk)
        self.assertEqual(producto.stock, 7)

    def test_seleccionar_mascota_la_guarda_en_la_factura(self):
        mascota = self._crear_mascota()
        self._sesion_con_producto(cantidad=1)
        self._elegir_cliente()
        response = self.client.post(
            reverse('billing:seleccionar_mascota'),
            {'mascota': f"{self.cliente.pk}:{mascota['_id']}"},
            follow=True,
        )
        self.assertContains(response, 'Vitamina B12')
        factura = models.Facturas.objects.get(estado='BORRADOR')
        self.assertEqual(factura.mascota['nombre'], 'Firulais')
        self.assertEqual(factura.mascota['especie'], 'Perro')
        self.assertEqual(factura.mascota['peso'], 10.5)

    def test_seleccionar_mascota_muestra_las_mascotas_del_cliente(self):
        self._crear_mascota()
        self._sesion_con_producto(cantidad=1)
        self._elegir_cliente()
        response = self.client.get(reverse('billing:seleccionar_mascota'))
        self.assertContains(response, 'Firulais')
        self.assertContains(response, 'Selecciona la mascota')

    def test_seleccionar_mascota_sin_datos_de_sesion_responde_404(self):
        response = self.client.get(reverse('billing:seleccionar_mascota'))
        self.assertEqual(response.status_code, 404)

    def test_anadir_otro_producto_usa_la_factura_existente(self):
        self._factura_borrador_con(cantidad=1)
        otro = self._crear_producto('Jeringa 5ml', 1500, 5)
        response = self.client.post(
            self._url_anadir(otro), {'cantidad': 2}, follow=True)
        factura = models.Facturas.objects.get(estado='BORRADOR')
        self.assertEqual(len(factura.factura_detalle), 2)
        jeringa = inventory.Productos.objects.get(pk=otro.pk)
        self.assertEqual(jeringa.stock, 3)

    def test_identificador_de_producto_invalido_responde_404(self):
        response = self.client.post(
            reverse('billing:añadir_item_inventario', args=['no-es-un-id']),
            {'cantidad': 1},
        )
        self.assertEqual(response.status_code, 404)

    # Carrito y factura ---------------------------------------------------
    def test_mostrar_carrito_lista_los_items(self):
        self._factura_borrador_con(cantidad=2)
        response = self.client.get(reverse('billing:mostrar_carrito'))
        self.assertContains(response, 'Vitamina B12')
        self.assertContains(response, '50000')
        self.assertNotContains(response, 'Tu carrito está vacío')

    def test_mostrar_carrito_vacio(self):
        response = self.client.get(reverse('billing:mostrar_carrito'))
        self.assertContains(response, 'Tu carrito está vacío')

    def test_finalizar_compra_calcula_iva_y_marca_pagada(self):
        self._factura_borrador_con(cantidad=2)
        response = self.client.post(reverse('billing:finalizar_compra'))
        self.assertRedirects(
            response,
            reverse('billing:listar_facturas'),
            fetch_redirect_response=False,
        )
        factura = models.Facturas.objects.get()
        self.assertEqual(factura.estado, 'PAGADA')
        self.assertEqual(factura.total, 50000)
        self.assertEqual(factura.iva, 9500.0)
        self.assertEqual(factura.subtotal, 40500.0)

    def test_listado_y_pdf_de_facturas(self):
        self._factura_borrador_con(cantidad=1)
        self.client.post(reverse('billing:finalizar_compra'), follow=True)
        respuesta = self.client.get(reverse('billing:listar_facturas'))
        self.assertContains(respuesta, 'Ana')
        factura = models.Facturas.objects.get()
        pdf = self.client.get(
            reverse('billing:generar_pdf_factura', args=[factura.pk]))
        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(pdf['Content-Type'], 'application/pdf')
        self.assertTrue(pdf.content.startswith(b'%PDF'))

