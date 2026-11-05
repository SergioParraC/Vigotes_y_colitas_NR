from django.test import TransactionTestCase
from django.urls import reverse

from . import models


class InventoryTestCase(TransactionTestCase):
    """Pruebas del CRUD de categorías, proveedores y productos del inventario.

    Se usa TransactionTestCase porque djongo no soporta transacciones: cada
    prueba deja los documentos en MongoDB y Django limpia las colecciones al
    terminar.
    """

    def setUp(self):
        self.categoria = models.Categoria()
        self.categoria.nombre = 'Medicamentos'
        self.categoria.descripcion = 'Medicamentos de uso veterinario'
        self.categoria.save()
        self.proveedor = self._crear_proveedor()

    def _crear_proveedor(self, nombre='Distribuidora Veterinaria SAS'):
        proveedor = models.Proveedor()
        proveedor.nombre = nombre
        proveedor.contacto = 'Ana Perez'
        proveedor.telefono = '3001234567'
        proveedor.email = 'ventas@distribuidora.com'
        proveedor.direccion = 'Calle 10 # 20-30'
        proveedor.save()
        return proveedor

    def _crear_producto(self, nombre='Vitamina B12', precio=25000, stock=10):
        producto = models.Productos()
        producto.nombre = nombre
        producto.categoria = {
            '_id': self.categoria.pk,
            'nombre': self.categoria.nombre,
            'descripcion': self.categoria.descripcion,
        }
        producto.proveedor = {
            '_id': self.proveedor.pk,
            'nombre': self.proveedor.nombre,
            'contacto': self.proveedor.contacto,
            'telefono': self.proveedor.telefono,
            'email': self.proveedor.email,
            'direccion': self.proveedor.direccion,
        }
        producto.descripcion = 'Suplemento vitaminico'
        producto.precio = precio
        producto.stock = stock
        producto.save()
        return producto

    def _datos_producto(self, nombre='Vitamina B12', precio=25000, stock=10):
        return {
            'nombre': nombre,
            'categoria': str(self.categoria.pk),
            'proveedor': str(self.proveedor.pk),
            'descripcion': 'Suplemento vitaminico',
            'precio': precio,
            'cantidad_en_stock': stock,
        }

    # Categorias -----------------------------------------------------------
    def test_crear_categoria(self):
        response = self.client.post(reverse('inventario:crear_categoria'), {
            'nombre': 'Alimentos',
            'descripcion': 'Alimento concentrado',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(models.Categoria.objects.filter(nombre='Alimentos').exists())

    def test_editar_categoria(self):
        url = reverse('inventario:guardar_categoria', args=[self.categoria.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(url, {
            'nombre': 'Medicamentos actualizados',
            'descripcion': 'Nueva descripcion',
        })
        self.assertEqual(response.status_code, 200)
        categoria = models.Categoria.objects.get(pk=self.categoria.pk)
        self.assertEqual(categoria.nombre, 'Medicamentos actualizados')

    # Proveedores ----------------------------------------------------------
    def test_crear_proveedor(self):
        response = self.client.post(reverse('inventario:crear_proveedor'), {
            'nombre': 'Laboratorios Vet',
            'contacto': 'Carlos Ruiz',
            'telefono': '3109876543',
            'email': 'contacto@labvet.com',
            'direccion': 'Carrera 45 # 12-10',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(models.Proveedor.objects.filter(nombre='Laboratorios Vet').exists())

    def test_editar_proveedor(self):
        url = reverse('inventario:guardar_proveedor', args=[self.proveedor.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(url, {
            'nombre': 'Distribuidora Actualizada',
            'contacto': 'Ana Perez',
            'telefono': '3001234567',
            'email': 'ventas@distribuidora.com',
            'direccion': 'Calle 10 # 20-30',
        })
        self.assertEqual(response.status_code, 200)
        proveedor = models.Proveedor.objects.get(pk=self.proveedor.pk)
        self.assertEqual(proveedor.nombre, 'Distribuidora Actualizada')

    def test_eliminar_proveedor(self):
        url = reverse('inventario:eliminar_proveedor', args=[self.proveedor.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.Proveedor.objects.filter(pk=self.proveedor.pk).exists())

    # Productos ------------------------------------------------------------
    def test_crear_producto_guarda_categoria_y_proveedor_embebidos(self):
        response = self.client.post(
            reverse('inventario:crear_producto_formulario'),
            self._datos_producto()
        )
        self.assertEqual(response.status_code, 302)
        producto = models.Productos.objects.get(nombre='Vitamina B12')
        self.assertEqual(producto.precio, 25000)
        self.assertEqual(producto.stock, 10)
        # La categoría y el proveedor quedan como documentos embebidos
        self.assertEqual(producto.categoria['_id'], self.categoria.pk)
        self.assertEqual(producto.categoria['nombre'], 'Medicamentos')
        self.assertEqual(producto.proveedor['_id'], self.proveedor.pk)
        self.assertEqual(producto.proveedor['nombre'], 'Distribuidora Veterinaria SAS')
        # La redirección lleva a la ventana de edición del producto creado
        self.assertEqual(
            response.url,
            reverse('inventario:guardar_producto', args=[producto.pk])
        )

    def test_editar_producto_actualiza_documentos_embebidos(self):
        producto = self._crear_producto()
        otra_categoria = models.Categoria()
        otra_categoria.nombre = 'Alimentos'
        otra_categoria.descripcion = 'Alimento concentrado'
        otra_categoria.save()
        url = reverse('inventario:guardar_producto', args=[producto.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        datos = self._datos_producto(nombre='Vitamina C', precio=32000, stock=25)
        datos['categoria'] = str(otra_categoria.pk)
        response = self.client.post(url, datos)
        self.assertEqual(response.status_code, 200)
        actualizado = models.Productos.objects.get(pk=producto.pk)
        self.assertEqual(actualizado.nombre, 'Vitamina C')
        self.assertEqual(actualizado.stock, 25)
        self.assertEqual(actualizado.categoria['nombre'], 'Alimentos')

    def test_listado_y_catalogo_de_productos(self):
        self._crear_producto()
        response = self.client.get(reverse('inventario:listado_productos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vitamina B12')
        self.assertEqual(response.context['Total'], 1)
        response = self.client.get(reverse('inventario:productos_cliente'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vitamina B12')

    def test_detalle_producto_cliente(self):
        producto = self._crear_producto()
        response = self.client.get(
            reverse('inventario:detalle_producto_cliente', args=[producto.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vitamina B12')
        self.assertContains(response, 'Medicamentos')

    def test_filtrar_productos_por_nombre_y_categoria(self):
        self._crear_producto(nombre='Vitamina B12')
        otra_categoria = models.Categoria()
        otra_categoria.nombre = 'Juguetes'
        otra_categoria.save()
        producto_juguete = self._crear_producto(nombre='Pelota', precio=8000)
        producto_juguete.categoria = {
            '_id': otra_categoria.pk,
            'nombre': otra_categoria.nombre,
            'descripcion': otra_categoria.descripcion,
        }
        producto_juguete.save()

        response = self.client.post(reverse('inventario:filtrar_productos'), {
            'nombre': 'Vitamina',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['Total'], 1)
        self.assertContains(response, 'Vitamina B12')

        response = self.client.post(reverse('inventario:filtrar_productos'), {
            'categoria': str(otra_categoria.pk),
        })
        self.assertEqual(response.context['Total'], 1)
        self.assertContains(response, 'Pelota')

        # El mismo filtro se puede pedir desde el catálogo del cliente
        response = self.client.post(reverse('inventario:filtrar_productos'), {
            'nombre': 'Vitamina',
            'origen_filtro': 'cliente',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['Total'], 1)
        self.assertContains(response, 'Catálogo de productos')
        self.assertContains(response, 'Vitamina B12')

    def test_eliminar_producto(self):
        producto = self._crear_producto()
        url = reverse('inventario:eliminar_producto', args=[producto.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(models.Productos.objects.filter(pk=producto.pk).exists())

    def test_identificadores_invalidos_o_inexistentes_responden_404(self):
        # Un texto que no es un ObjectId válido
        response = self.client.get(
            reverse('inventario:guardar_categoria', args=['no-es-un-objectid'])
        )
        self.assertEqual(response.status_code, 404)
        # Un ObjectId válido pero sin documento asociado
        response = self.client.get(
            reverse('inventario:detalle_producto_cliente', args=['6aeacb1e0d177973ee271904'])
        )
        self.assertEqual(response.status_code, 404)

    # Paginas --------------------------------------------------------------
    def test_paginas_de_listado_y_creacion_responden_200(self):
        self._crear_producto()
        for nombre in (
            'inventario:listado_categorias',
            'inventario:crear_categoria',
            'inventario:listado_proveedores',
            'inventario:crear_proveedor',
            'inventario:listado_productos',
            'inventario:crear_producto_formulario',
            'inventario:productos_cliente',
        ):
            response = self.client.get(reverse(nombre))
            self.assertEqual(response.status_code, 200, nombre)
        # Los listados muestran los documentos creados
        response = self.client.get(reverse('inventario:listado_categorias'))
        self.assertContains(response, 'Medicamentos')
        response = self.client.get(reverse('inventario:listado_proveedores'))
        self.assertContains(response, 'Distribuidora Veterinaria SAS')

    def test_exportar_pdf_de_productos_y_proveedores(self):
        self._crear_producto()
        for nombre, args in (
            ('inventario:pdf_productos', []),
            ('inventario:pdf_proveedores', []),
        ):
            response = self.client.get(reverse(nombre, args=args))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertTrue(response.content.startswith(b'%PDF'))

