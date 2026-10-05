from djongo import models
from ..customers import models as customers
from ..meeting import models as meetings
from ..inventory import models as product

class FacturaDetalle(models.Model):
    cita = models.EmbeddedField(model_container=meetings.Citas)
    vacuna = models.EmbeddedField(model_container=meetings.Vacunas)
    producto = models.EmbeddedField(model_container=product.Productos)
    descripción = models.CharField(
        max_length=150,
        null=True
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        null=True
    )
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
            abstract = True
    
class Facturas(models.Model):

    class EstadosFactura(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PAGADA = 'PAGADA', 'Pagada'
        CANCELADA = 'CANCELADA', 'Cancelada'
    factura_detalle = models.ArrayField(model_container=FacturaDetalle)
    cliente = models.EmbeddedField(model_container=customers.Cliente)
    fecha = models.DateTimeField(null=False)
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    iva = models.DecimalField(
        max_digits=2, 
        decimal_places=2, 
        default=0
    )
    total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0
    )
    estado = models.CharField(
        max_length=20, 
        choices=EstadosFactura, 
        default=EstadosFactura.BORRADOR
    )

    class Meta:
            abstract = True
