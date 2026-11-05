from djongo import models
from ..customers import models as customers
from ..meeting import models as meetings
from ..inventory import models as product
from ..pets import models as pets

class FacturaDetalle(models.Model):
    """
    Contenedor de los ítems que se guardan dentro de ``Facturas``.
    """

    cita = models.EmbeddedField(
        model_container=meetings.Citas,
        null=True,
        blank=True
    )
    vacuna = models.EmbeddedField(
        model_container=meetings.Vacunas,
        null=True,
        blank=True
    )
    producto = models.EmbeddedField(
        model_container=product.Productos,
        null=True,
        blank=True
    )
    descripcion = models.CharField(
        max_length=150,
        null=True
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        null=True
    )
    # Debuelve los valores que corresponde según se requiera
    precio_unitario = models.FloatField()
    subtotal = models.FloatField()

    class Meta:
            abstract = True
    
class Facturas(models.Model):

    class EstadosFactura(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PAGADA = 'PAGADA', 'Pagada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    _id = models.ObjectIdField()
    factura_detalle = models.ArrayField(model_container=FacturaDetalle)
    cliente = models.EmbeddedField(model_container=customers.Cliente)
    mascota = models.EmbeddedField(
        model_container=pets.Mascotas,
        null=True,
        blank=True
    )
    fecha = models.DateTimeField(null=False)
    subtotal = models.FloatField(
        default=0
    )
    iva = models.FloatField(
        default=0
    )
    total = models.FloatField(
        default=0
    )
    estado = models.CharField(
        max_length=20, 
        choices=EstadosFactura.choices, 
        default=EstadosFactura.BORRADOR
    )

    class Meta:
        db_table = 'facturas'

    def __str__(self):
        return f'Factura {self.pk} - {self.estado}'

