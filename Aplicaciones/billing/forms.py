from django import forms

from ..customers.models import Cliente
from ..inventory.forms import ObjectIdModelChoiceField

'''Muestra los clientes para crear la factura'''
class CrearFacturaClienteForm(forms.Form):
    """Selecciona el cliente al que se le factura.

    Se reutiliza ``ObjectIdModelChoiceField`` del módulo de inventario porque
    djongo no convierte el texto del formulario al ObjectId del documento.
    """

    cliente = ObjectIdModelChoiceField(
        label="Cliente",
        queryset=Cliente.objects.all(),
        empty_label="Selecciona un cliente"
    )
