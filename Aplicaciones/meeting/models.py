from djongo import models

class HistorialMedico(models.Model):
    
    alergias = models.CharField(
        verbose_name = 'Alergias', 
        max_length=100,
        null=False
    )
    fecha_visita = models.DateField(
        auto_now_add=True
    )
    motivo_visita = models.CharField(
        verbose_name = 'Motivo de la visita', 
        max_length=100,
        null=False
    )
    diagnostico = models.CharField(
        verbose_name = 'Diagnostico', 
        max_length=100,
        null=False
    )
    tratamiento = models.CharField(
        verbose_name = 'Tratamiento', 
        max_length=100,
        null=False
    )

    class Meta:
            abstract = True

class Citas(models.Model):

    class EstadosCita(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'
    
    fecha = models.DateTimeField(null=False)
    motivo = models.CharField(
        verbose_name = 'Motivo de cita', 
        max_length=100,
        null=False
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadosCita.choices,
        default=EstadosCita.PENDIENTE,
    )
    veterinario = models.CharField(
        max_length=30,
        null=False
    )

    class Meta:
            abstract = True

class Vacunas(models.Model):

    nombre_vacuna = models.CharField(
        max_length=15,
        null=False
    )
    fecha_aplicacion = models.DateField()
    veterinario = models.CharField(
        max_length=30,
        null=False
    )

    class Meta:
            abstract = True