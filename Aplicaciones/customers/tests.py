from django.test import TransactionTestCase
from django.urls import resolve, reverse

from . import models


class HomeTestCase(TransactionTestCase):
    """Pruebas de la página principal y del formulario de contacto.

    Se usa ``TransactionTestCase`` porque djongo (MongoDB) no soporta
    transacciones.
    """

    def test_home_responde_y_muestra_el_hero(self):
        response = self.client.get(reverse('customers:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['titlePage'], 'Veterinaria Vida Animal')
        self.assertContains(response, 'Cuidamos la salud de tus mascotas')
        self.assertContains(response, 'Nuestros servicios')

    def test_home_tambien_responde_en_slash_home(self):
        response = self.client.get(reverse('customers:home_directo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cuidamos la salud de tus mascotas')

    def test_la_raiz_del_proyecto_es_el_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'home.html')
        self.assertContains(response, 'Nuestros servicios')

    def test_contacto_muestra_el_formulario(self):
        response = self.client.get(reverse('customers:contacto'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['titlePage'], 'Contacto')
        for campo in ('nombre', 'numero_contacto', 'email', 'mensaje'):
            self.assertContains(response, f'name="{campo}"')

    def test_contacto_guarda_el_mensaje(self):
        response = self.client.post(reverse('customers:contacto'), {
            'nombre': 'Ana',
            'numero_contacto': '3001234567',
            'email': 'ana@correo.com',
            'mensaje': 'Quiero agendar una cita para mi mascota',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tu mensaje fue enviado correctamente.')
        contacto = models.Contacto.objects.get()
        self.assertEqual(contacto.nombre, 'Ana')
        self.assertEqual(contacto.numero_contacto, '3001234567')
        self.assertEqual(contacto.email, 'ana@correo.com')
        self.assertIn('Quiero agendar una cita', contacto.mensaje)

    def test_contacto_con_email_invalido_no_guarda(self):
        response = self.client.post(reverse('customers:contacto'), {
            'nombre': 'Ana',
            'numero_contacto': '3001234567',
            'email': 'no-es-un-correo',
            'mensaje': 'Quiero agendar una cita',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(models.Contacto.objects.exists())
        self.assertIn('email', response.context['formulario_contacto'].errors)

    def test_los_botones_del_header_tienen_destino(self):
        contenido = self.client.get('/').content.decode('utf-8')
        destinos = [
            '/', '/pets/', '/inventario/listado-productos/', '/inventario/',
            '/inventario/carrito/listar-facturas/', '/citas/', '/contacto/',
        ]
        for destino in destinos:
            self.assertIn(f'href="{destino}"', contenido)
            # resolve lanza Resolver404 si el botón no lleva a ninguna vista
            resolve(destino)
        # El botón de inicio de sesión se retiró: no existe la app de usuarios
        self.assertNotIn('/users/usuario/', contenido)

