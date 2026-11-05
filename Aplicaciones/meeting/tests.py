from datetime import date, time

from bson.objectid import ObjectId
from django.test import TransactionTestCase
from django.urls import reverse

from ..customers import models as customers


class CitasTestCase(TransactionTestCase):
    """Pruebas del CRUD de citas (van embebidas en la mascota del cliente)."""

    def setUp(self):
        self.mascota_id = ObjectId()
        self.cliente = customers.Cliente()
        self.cliente.nombre = 'Ana'
        self.cliente.apellido = 'Perez'
        self.cliente.tipo_documento = 'CC'
        self.cliente.numero_documeto = '10203040'
        self.cliente.email = 'ana@correo.com'
        self.cliente.telefono = '3001234567'
        self.cliente.direccion = 'Calle 1 # 2-3'
        self.cliente.mascotas = [{
            '_id': self.mascota_id,
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

    def _mascota(self):
        return customers.Cliente.objects.get(pk=self.cliente.pk).mascotas[0]

    def _datos_cita(self, **cambios):
        datos = {
            'Mascota': f'{self.cliente.pk}:{self.mascota_id}',
            'Tipo': 'Consulta',
            'FechaCita': '2026-11-20',
            'HoraCita': '09:30',
            'Estado': 'PENDIENTE',
            'Motivo': 'Control',
            'Sintomas': 'Decaimiento',
            'Notas': 'Sin novedad',
            'Veterinario': 'Dra. Ruiz',
        }
        datos.update(cambios)
        return datos

    def _crear_cita(self, **cambios):
        return self.client.post(
            reverse('citas:crear_cita'),
            self._datos_cita(**cambios),
            follow=True,
        )

    def test_listado_sin_citas(self):
        response = self.client.get(reverse('citas:listado_citas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No hay citas registradas')

    def test_crear_cita_la_guarda_en_la_mascota(self):
        response = self._crear_cita()
        self.assertContains(response, 'Cita creada correctamente')
        citas = self._mascota()['citas']
        self.assertEqual(len(citas), 1)
        self.assertEqual(citas[0]['tipo'], 'Consulta')
        self.assertEqual(citas[0]['hora_cita'], time(9, 30))
        self.assertEqual(citas[0]['estado'], 'PENDIENTE')
        self.assertEqual(citas[0]['sintomas'], 'Decaimiento')

    def test_detalle_y_edicion_de_la_cita(self):
        self._crear_cita()
        cita = self._mascota()['citas'][0]
        detalle = self.client.get(
            reverse('citas:detalle_cita', args=[cita['_id']]))
        self.assertEqual(detalle.status_code, 200)
        self.assertContains(detalle, 'Firulais')

        response = self.client.post(
            reverse('citas:detalle_cita', args=[cita['_id']]),
            self._datos_cita(Estado='COMPLETADA', Sintomas='Recuperado'),
        )
        self.assertContains(response, 'Cita editada exitosamente')
        actualizada = self._mascota()['citas'][0]
        self.assertEqual(actualizada['estado'], 'COMPLETADA')
        self.assertEqual(actualizada['sintomas'], 'Recuperado')

    def test_filtrar_citas_por_nombre_y_estado(self):
        self._crear_cita()
        response = self.client.get(
            reverse('citas:filtrar_citas'), {'nombre': 'firulais'})
        self.assertContains(response, 'Firulais')

        response = self.client.get(
            reverse('citas:filtrar_citas'), {'nombre': 'inexistente'})
        self.assertNotContains(response, 'Firulais')

        response = self.client.get(
            reverse('citas:filtrar_citas'), {'estado': 'COMPLETADA'})
        self.assertNotContains(response, 'Firulais')

    def test_eliminar_cita(self):
        self._crear_cita()
        cita = self._mascota()['citas'][0]
        response = self.client.post(
            reverse('citas:eliminar_cita', args=[cita['_id']]),
            follow=True,
        )
        self.assertContains(response, 'Cita eliminada exitosamente')
        self.assertEqual(self._mascota()['citas'], [])

    def test_crear_cita_sin_mascota_avisa(self):
        response = self.client.post(
            reverse('citas:crear_cita'),
            self._datos_cita(Mascota=''),
            follow=True,
        )
        self.assertContains(response, 'Selecciona la mascota de la cita')
        self.assertEqual(self._mascota()['citas'], [])

    def test_cita_inexistente_responde_404(self):
        response = self.client.get(
            reverse('citas:detalle_cita', args=['no-es-un-id']))
        self.assertEqual(response.status_code, 404)

