from djongo import models
from ..meeting import models as mt

class Mascotas(models.Model):

    _id = models.ObjectIdField()
    historia_clinica = models.ArrayField(model_container=mt.HistorialMedico)
    vacunas = models.ArrayField(model_container=mt.Vacunas)
    citas = models.ArrayField(model_container=mt.Citas)
    
    nombre = models.CharField(
        verbose_name = 'Nombre mascota', 
        max_length=50,
        null=False
    )
    especie = models.CharField(
        verbose_name = 'Especie de la mascota', 
        max_length=50,
        null=False
    )
    raza = models.CharField(
        verbose_name = 'Raza de la mascota', 
        max_length=50,
        null=True,
        blank=True
    )
    fecha_nacimiento = models.DateField(
        null = True
    )
    peso = models.FloatField(
        verbose_name="Peso de la mascota",
        default=0,
    )
    vacunado = models.BooleanField(default=False)
    
    class Meta:
            abstract = True