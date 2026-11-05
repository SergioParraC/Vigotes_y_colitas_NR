from djongo import models
from ..pets import models as pets

class Cliente(models.Model):
    """
    Colección 'clientes'.
    """

    class TipoDocumento(models.TextChoices):
        CEDULA = 'CC', 'Cédula de Ciudadanía'
        PASAPORTE = 'PAS', 'Pasaporte'
        DNI = 'DNI', 'Documento Nacional de Identidad'
        CEDULA_EXTRANJERIA = 'CE', 'Cédula de Extranjería'

    _id = models.ObjectIdField()
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
    direccion = models.CharField(
        verbose_name="Dirección", 
        max_length=200, 
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return f'{self.nombre} {self.apellido}'


class Contacto(models.Model):
    """
    Colección 'contactos': mensajes enviados desde el formulario de contacto.
    """

    _id = models.ObjectIdField()
    nombre = models.CharField(
        verbose_name='Nombre',
        max_length=100,
        null=False
    )
    numero_contacto = models.CharField(
        verbose_name='Número de contacto',
        max_length=20,
        null=False
    )
    email = models.EmailField(
        verbose_name='Correo electrónico',
        null=False
    )
    mensaje = models.TextField(
        verbose_name='Mensaje',
        null=False
    )

    class Meta:
        db_table = 'contactos'

    def __str__(self):
        return f'Contacto de {self.nombre} - {self.email}'

