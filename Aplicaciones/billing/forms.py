from bson.errors import InvalidId
from bson.objectid import ObjectId
from django import forms
from django.http import Http404
from django.utils import timezone

from . import models
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


'''Copia del cliente que se guarda dentro de la factura'''
def documento_de_cliente(cliente):
    """djongo exige el documento completo de cada campo embebido."""
    return {
        '_id': cliente.pk,
        'mascotas': [],
        'nombre': cliente.nombre,
        'apellido': cliente.apellido,
        'tipo_documento': cliente.tipo_documento,
        'numero_documeto': cliente.numero_documeto,
        'email': cliente.email,
        'telefono': cliente.telefono,
        'direccion': cliente.direccion,
    }


'''Copia del producto que se guarda dentro del ítem de la factura'''
def documento_de_producto(producto):
    """Copia el producto con su categoria y su proveedor ya normalizados."""
    categoria = producto.categoria or {}
    proveedor = producto.proveedor or {}
    # El producto puede traer los documentos embebidos o los modelos sueltos
    if not isinstance(categoria, dict):
        categoria = {
            '_id': categoria.pk,
            'nombre': categoria.nombre,
            'descripcion': categoria.descripcion,
        }
    if not isinstance(proveedor, dict):
        proveedor = {
            '_id': proveedor.pk,
            'nombre': proveedor.nombre,
            'contacto': proveedor.contacto,
            'telefono': proveedor.telefono,
            'email': proveedor.email,
            'direccion': proveedor.direccion,
        }
    return {
        '_id': producto.pk,
        'nombre': producto.nombre,
        'categoria': categoria,
        'proveedor': proveedor,
        'descripcion': producto.descripcion,
        'precio': producto.precio,
        'stock': producto.stock,
        'img': producto.img.name if producto.img else '',
    }


'''Item del carrito con la copia del producto'''
def detalle_de_producto(producto, cantidad):
    """Arma el ítem que se guarda dentro del arreglo de la factura."""
    cantidad = int(cantidad or 1)
    return {
        'cita': None,
        'vacuna': None,
        'producto': documento_de_producto(producto),
        'descripcion': producto.nombre,
        'cantidad': cantidad,
        'precio_unitario': producto.precio,
        'subtotal': producto.precio * cantidad,
    }


'''Muestra las mascotas del cliente seleccionado y arma la factura'''
class CrearFacturaMascotaForm(forms.Form):
    """Selecciona la mascota del cliente (puede quedar sin mascota)."""

    mascota = forms.ChoiceField(
        label="Mascota",
        choices=(),
        required=False
    )

    # Método donde se filtran las mascotas por cliente
    def __init__(
            self, *args, cliente_id=None, producto=None, cantidad=1, **kwargs):
        super().__init__(*args, **kwargs)
        # Producto y cantidad con los que se crea el primer ítem del carrito
        self.producto = producto
        self.cantidad = int(cantidad or 1)
        # Las mascotas van embebidas en el cliente, así que se trae el cliente
        # completo: sus mascotas para el desplegable y su copia para la factura
        try:
            self.cliente = Cliente.objects.get(pk=ObjectId(str(cliente_id)))
        except (InvalidId, TypeError):
            raise Http404('El identificador del cliente no es válido')
        except Cliente.DoesNotExist:
            raise Http404('El cliente seleccionado no existe')
        opciones = [('', 'Selecciona la mascota')]
        # El valor del desplegable lleva el cliente y el _id de la mascota
        for documento in (self.cliente.mascotas or []):
            opciones.append((
                f"{self.cliente.pk}:{documento.get('_id')}",
                documento.get('nombre'),
            ))
        self.fields['mascota'].choices = opciones

    def _documento_mascota(self):
        """Copia la mascota elegida, si no se eligió ninguna queda None."""
        valor = self.cleaned_data.get('mascota')
        if not valor:
            return None
        _, id_mascota = valor.split(':', 1)
        for documento in (self.cliente.mascotas or []):
            if str(documento.get('_id')) == str(id_mascota):
                return {
                    '_id': documento.get('_id'),
                    'historia_clinica': documento.get(
                        'historia_clinica') or [],
                    'vacunas': documento.get('vacunas') or [],
                    'citas': documento.get('citas') or [],
                    'nombre': documento.get('nombre'),
                    'especie': documento.get('especie'),
                    'raza': documento.get('raza'),
                    'fecha_nacimiento': documento.get('fecha_nacimiento'),
                    'peso': documento.get('peso'),
                    'vacunado': documento.get('vacunado'),
                }
        return None

    def save(self):
        """Crea la factura en BORRADOR con el cliente, la mascota y el ítem."""
        factura = models.Facturas()
        factura.cliente = documento_de_cliente(self.cliente)
        factura.mascota = self._documento_mascota()
        factura.factura_detalle = [
            detalle_de_producto(self.producto, self.cantidad)
        ]
        factura.fecha = timezone.now()
        factura.save()
        return factura
