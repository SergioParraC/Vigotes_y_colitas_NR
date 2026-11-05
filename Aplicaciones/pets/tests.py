from django.test import TransactionTestCase
from django.urls import reverse

from ..customers import models as customers


class MascotasTestCase(TransactionTestCase):
    """Pruebas del CRUD de mascotas (van embebidas en el cliente)."""

    def setUp(self):
        # Cada prueba crea su propio dueño y mascota con el formulario
        pass

    def _datos_mascota(self, **cambios):
        datos = {
            'dueno-nombre': 'Ana',
            'dueno-apellido': 'Perez',
            'dueno-tipo_documento': 'CC',
            'dueno-numero_documeto': '10203040',
            'dueno-telefono': '3001234567',
            'dueno-email': 'ana@correo.com',
            'dueno-direccion': 'Calle 1 # 2-3',
            'mascota-nombre': 'Firulais',
            'mascota-especie': 'Perro',
            'mascota-raza': 'Criollo',
            'mascota-fecha_nacimiento': '2020-01-01',
            'mascota-peso': '10.5',
            'mascota-vacunado': 'on',
        }
        datos.update(cambios)
        return datos

    def _registrar(self, **cambios):
        return self.client.post(
            reverse('pets:crear_mascota'),
            self._datos_mascota(**cambios),
        )

    def _cliente_guardado(self):
        return customers.Cliente.objects.get(numero_documeto='10203040')

    def _mascota_guardada(self):
        return self._cliente_guardado().mascotas[0]

    def test_listado_de_mascotas_vacio(self):
        response = self.client.get(reverse('pets:listado_mascotas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gestión de mascotas')
        self.assertContains(response, 'No hay mascotas registradas')

    def test_registrar_mascota_crea_el_dueno_y_la_mascota(self):
        response = self._registrar()
        self.assertRedirects(response, reverse('pets:listado_mascotas'))
        cliente = customers.Cliente.objects.get(numero_documeto='10203040')
        self.assertEqual(cliente.nombre, 'Ana')
        self.assertEqual(cliente.apellido, 'Perez')
        self.assertEqual(cliente.email, 'ana@correo.com')
        mascota = cliente.mascotas[0]
        self.assertEqual(mascota['nombre'], 'Firulais')
        self.assertEqual(mascota['especie'], 'Perro')
        self.assertEqual(mascota['peso'], 10.5)
        self.assertTrue(mascota['vacunado'])
        self.assertEqual(mascota['citas'], [])
        self.assertEqual(mascota['vacunas'], [])

    def test_historia_muestra_los_datos_de_la_mascota(self):
        self._registrar()
        mascota = self._mascota_guardada()
        response = self.client.get(
            reverse('pets:historia_mascota', args=[mascota['_id']]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Firulais')
        self.assertContains(response, 'Ana Perez')
        self.assertContains(response, 'No hay citas registradas')

    def test_editar_mascota_permite_editar_dueno_y_mascota(self):
        self._registrar()
        mascota = self._mascota_guardada()
        url = reverse('pets:editar_mascota', args=[mascota['_id']])

        # el mismo formulario de dos secciones, precargado
        detalle = self.client.get(url)
        self.assertContains(detalle, 'Datos del dueño')
        self.assertContains(detalle, 'Datos de la mascota')
        self.assertContains(detalle, 'value="Ana"')
        self.assertContains(detalle, 'value="Firulais"')

        response = self.client.post(url, self._datos_mascota(**{
            'dueno-apellido': 'Gomez',
            'mascota-nombre': 'Firulais II',
            'mascota-peso': '12',
        }), follow=True)
        self.assertRedirects(
            response,
            reverse('pets:historia_mascota', args=[mascota['_id']]),
            fetch_redirect_response=False,
        )
        cliente = self._cliente_guardado()
        self.assertEqual(cliente.apellido, 'Gomez')
        self.assertEqual(cliente.mascotas[0]['nombre'], 'Firulais II')
        self.assertEqual(cliente.mascotas[0]['peso'], 12)

    def test_registrar_vacuna_la_guarda_en_la_mascota(self):
        self._registrar()
        mascota = self._mascota_guardada()
        response = self.client.post(
            reverse('pets:crear_vacuna'),
            {
                'mascota': f"{self._cliente_guardado().pk}:{mascota['_id']}",
                'nombre_vacuna': 'Rabia',
                'fecha_aplicacion': '2025-05-01',
                'veterinario': 'Dra. Ruiz',
            },
        )
        self.assertRedirects(response, reverse('pets:listado_mascotas'))
        vacunas = self._mascota_guardada()['vacunas']
        self.assertEqual(len(vacunas), 1)
        self.assertEqual(vacunas[0]['nombre_vacuna'], 'Rabia')

    def test_editar_vacuna_actualiza_el_subdocumento(self):
        self._registrar()
        mascota = self._mascota_guardada()
        self.client.post(
            reverse('pets:crear_vacuna'),
            {
                'mascota': f"{self._cliente_guardado().pk}:{mascota['_id']}",
                'nombre_vacuna': 'Rabia',
                'fecha_aplicacion': '2025-05-01',
                'veterinario': 'Dra. Ruiz',
            },
            follow=True,
        )
        vacuna = self._mascota_guardada()['vacunas'][0]
        response = self.client.post(
            reverse('pets:editar_vacuna', args=[vacuna['_id']]),
            {
                'mascota': f"{self._cliente_guardado().pk}:"
                           f"{self._mascota_guardada()['_id']}",
                'nombre_vacuna': 'Rabia refuerzo',
                'fecha_aplicacion': '2025-06-01',
                'veterinario': 'Dra. Ruiz',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            self._mascota_guardada()['vacunas'][0]['nombre_vacuna'],
            'Rabia refuerzo'
        )

    def test_registrar_historial_lo_guarda_en_la_mascota(self):
        self._registrar()
        mascota = self._mascota_guardada()
        response = self.client.post(
            reverse('pets:crear_historial'),
            {
                'mascota': f"{self._cliente_guardado().pk}:{mascota['_id']}",
                'alergias': 'Ninguna',
                'fecha_visita': '2025-05-01',
                'motivo_visita': 'Control',
                'diagnostico': 'Sano',
                'tratamiento': 'Ninguno',
            },
        )
        self.assertRedirects(response, reverse('pets:listado_mascotas'))
        historiales = self._mascota_guardada()['historia_clinica']
        self.assertEqual(len(historiales), 1)
        self.assertEqual(historiales[0]['diagnostico'], 'Sano')

    def test_editar_historial_actualiza_el_subdocumento(self):
        self._registrar()
        mascota = self._mascota_guardada()
        self.client.post(
            reverse('pets:crear_historial'),
            {
                'mascota': f"{self._cliente_guardado().pk}:{mascota['_id']}",
                'alergias': 'Ninguna',
                'fecha_visita': '2025-05-01',
                'motivo_visita': 'Control',
                'diagnostico': 'Sano',
                'tratamiento': 'Ninguno',
            },
            follow=True,
        )
        historial = self._mascota_guardada()['historia_clinica'][0]
        response = self.client.post(
            reverse('pets:editar_historial', args=[historial['_id']]),
            {
                'mascota': f"{self._cliente_guardado().pk}:"
                           f"{self._mascota_guardada()['_id']}",
                'alergias': 'Polvo',
                'fecha_visita': '2025-06-01',
                'motivo_visita': 'Revisión',
                'diagnostico': 'Alergia',
                'tratamiento': 'Antihistamínico',
            },
        )
        self.assertEqual(response.status_code, 302)
        actualizado = self._mascota_guardada()['historia_clinica'][0]
        self.assertEqual(actualizado['diagnostico'], 'Alergia')

    def test_mascota_inexistente_responde_404(self):
        response = self.client.get(
            reverse('pets:historia_mascota', args=['no-es-un-id']))
        self.assertEqual(response.status_code, 404)

