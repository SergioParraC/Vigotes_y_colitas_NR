from djongo import models
from ..meeting import models as mt

class Mascotas(models.Model):

    historia_clinica = models.ArrayField(model_container=mt.HistorialMedico)
    vacunas = models.ArrayField(model_container=mt.Vacunas)
    citas = models.ArrayField(model_container=mt.Citas)
    
    nombre = models.CharField(
        verbose_name = 'Nombre mascota', 
        max_length=15,
        null=False
    )
    especie = models.CharField(
        verbose_name = 'Especie de la mascota', 
        max_length=15,
        null=False
    )
    raza = models.CharField(
        verbose_name = 'Nombres de la persona', 
        max_length=15,
        null=True
    )
    fecha_nacimiento = models.DateField(
        null = True
    )
    peso = models.DecimalField(
        verbose_name="Peso de la mascota",
        max_digits=3, 
        decimal_places=2,
    )
    vacunado = models.BooleanField(default=False)
    
    class Meta:
            abstract = True