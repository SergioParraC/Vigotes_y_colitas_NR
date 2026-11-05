from datetime import date

from djongo import models

class HistorialMedico(models.Model):

    _id = models.ObjectIdField()
    alergias = models.CharField(
        verbose_name = 'Alergias', 
        max_length=250,
        null=True,
        blank=True
    )
    # El origen permitía elegir la fecha de la visita; ``auto_now_add`` la
    # fijaba sola y no se podía editar.
    fecha_visita = models.DateField(default=date.today)
    motivo_visita = models.CharField(
        verbose_name = 'Motivo de la visita', 
        max_length=200,
        null=False
    )
    diagnostico = models.CharField(
        verbose_name = 'Diagnostico', 
        max_length=250,
        null=False
    )
    tratamiento = models.CharField(
        verbose_name = 'Tratamiento', 
        max_length=250,
        null=False
    )

    class Meta:
            abstract = True

class Citas(models.Model):

    class EstadosCita(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    class TiposCita(models.TextChoices):
        CONSULTA = 'Consulta', 'Consulta General'
        VACUNACION = 'Vacunación', 'Vacunación'
        CIRUGIA = 'Cirugía', 'Cirugía'
        PELUQUERIA = 'Peluqueria', 'Peluqueria'
        CONTROL = 'Control', 'Control'
        EMERGENCIA = 'Emergencia', 'Emergencia'

    _id = models.ObjectIdField()
    tipo = models.CharField(
        max_length=50,
        choices=TiposCita.choices,
        default=TiposCita.CONSULTA,
        verbose_name='Tipo de Cita'
    )
    fecha = models.DateTimeField(
        verbose_name='Fecha de la Cita',
        null=False
    )
    hora_cita = models.TimeField(
        verbose_name='Hora de la Cita',
        null=True,
        blank=True
    )
    motivo = models.CharField(
        verbose_name = 'Motivo de cita', 
        max_length=200,
        null=True,
        blank=True
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadosCita.choices,
        default=EstadosCita.PENDIENTE,
    )
    sintomas = models.CharField(
        verbose_name='Síntomas de la Mascota',
        max_length=250,
        null=True,
        blank=True
    )
    notas = models.CharField(
        verbose_name='Notas Adicionales',
        max_length=250,
        null=True,
        blank=True
    )
    veterinario = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
            abstract = True

class Vacunas(models.Model):

    _id = models.ObjectIdField()
    nombre_vacuna = models.CharField(
        max_length=100,
        null=False
    )
    fecha_aplicacion = models.DateField()
    veterinario = models.CharField(
        max_length=100,
        null=False
    )

    class Meta:
            abstract = True