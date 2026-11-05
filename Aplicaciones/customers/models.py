from djongo import models
from ..pets import models as pets

class Cliente(models.Model):
    """Colección 'clientes'.

    Además de ser una colección propia (de aquí se eligen los clientes al
    facturar), se usa como contenedor del campo embebido ``Facturas.cliente``,
    igual que ``Categoria`` lo es de ``Productos.categoria``.
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
        max_length=20, 
        null=True
    )

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

