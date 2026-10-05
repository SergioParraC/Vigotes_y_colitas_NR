from djongo import models
from ..pets import models as pets

class Cliente(models.Model):

    class TipoDocumento(models.TextChoices):
        CEDULA = 'CC', 'Cédula de Ciudadanía'
        PASAPORTE = 'PAS', 'Pasaporte'
        DNI = 'DNI', 'Documento Nacional de Identidad'
        CEDULA_EXTRANJERIA = 'CE', 'Cédula de Extranjería'

    mascotas = models.ArrayField(model_container=pets.Mascotas)
    nombre = models.CharField(
        verbose_name = 'Nombres de la persona', 
        max_length=15,
        null=False
    )
    apellido = models.CharField(
        verbose_name = 'Apellidos de la persona', 
        max_length=15,
        null=False
    )
    tipo_documento = models.CharField(
        max_length=3,
        choices=TipoDocumento.choices,
        default=TipoDocumento.CEDULA,
    )
    numero_documeto = models.CharField(
        verbose_name = 'Número de documento', 
        max_length=15,
        null=False
    )
    email = models.EmailField(
        verbose_name="Persona de contacto", 
        null=False
    )
    telefono = models.CharField(
        verbose_name="Número de contacto", 
        max_length=25, 
        null=False
    )
    dirección = models.CharField(
        verbose_name="Número de contacto", 
        max_length=20, 
        null=True
    )

    class Meta:
            abstract = True
