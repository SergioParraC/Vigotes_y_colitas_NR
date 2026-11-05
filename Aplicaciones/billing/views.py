from io import BytesIO

from bson.errors import InvalidId
from bson.objectid import ObjectId
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from xhtml2pdf import pisa

from . import forms, models
from ..inventory import models as inventory

def _a_object_id(id_texto):
    """
    Convierte el identificador recibido por la URL al ObjectId.
    """
    try:
        return ObjectId(str(id_texto))
    except (InvalidId, TypeError):
        raise Http404('El identificador del documento no es válido')


def _obtener_documento(modelo, id_texto):
    """Busca un documento por su _id y responde 404 si no existe."""
    try:
        return modelo.objects.get(pk=_a_object_id(id_texto))
    except modelo.DoesNotExist:
        raise Http404('El documento solicitado no existe')


def _campo(documento, nombre):
    """
    Lee un campo de un documento embebido.
    """
    if documento is None:
        return None
    if isinstance(documento, dict):
        return documento.get(nombre)
    return getattr(documento, nombre, None)


def _factura_borrador():
    """Devuelve el carrito: la factura que está en estado BORRADOR."""
    return models.Facturas.objects.filter(
        estado=models.Facturas.EstadosFactura.BORRADOR
    ).first()


def _documento_cliente(cliente):
    """
    Copia del cliente que se guarda dentro de la factura.
    """
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


def _documento_producto(producto):
    """Copia del producto que se guarda dentro del ítem de la factura."""
    categoria = producto.categoria
    proveedor = producto.proveedor
    return {
        '_id': producto.pk,
        'nombre': producto.nombre,
        'categoria': {
            '_id': _campo(categoria, '_id'),
            'nombre': _campo(categoria, 'nombre'),
            'descripcion': _campo(categoria, 'descripcion'),
        },
        'proveedor': {
            '_id': _campo(proveedor, '_id'),
            'nombre': _campo(proveedor, 'nombre'),
            'contacto': _campo(proveedor, 'contacto'),
            'telefono': _campo(proveedor, 'telefono'),
            'email': _campo(proveedor, 'email'),
            'direccion': _campo(proveedor, 'direccion'),
        },
        'descripcion': producto.descripcion,
        'precio': producto.precio,
        'stock': producto.stock,
        'img': producto.img.name or '',
    }


def _nuevo_detalle(producto, cantidad):
    """Arma el ítem del carrito con la copia del producto."""
    return {
        'cita': None,
        'vacuna': None,
        'producto': _documento_producto(producto),
        'descripcion': producto.nombre,
        'cantidad': cantidad,
        'precio_unitario': producto.precio,
        'subtotal': producto.precio * cantidad,
    }


def _descontar_stock(producto, cantidad):
    """Disminuye las unidades disponibles del producto."""
    producto.stock = producto.stock - cantidad
    producto.save()


def _agregar_detalle(factura, detalle):
    """Añade un ítem al arreglo ``factura_detalle`` y guarda la factura.

    En Mongo los ítems no son una colección aparte: van embebidos en el
    documento de la factura, por eso se reescribe el arreglo completo.
    """
    detalles = list(factura.factura_detalle or [])
    detalles.append(detalle)
    factura.factura_detalle = detalles
    factura.save()


def _producto_de_sesion(request):
    """Trae el producto que se guardó en sesión al iniciar la compra."""
    id_producto = request.session.get('id_producto')
    if not id_producto:
        return None
    try:
        return inventory.Productos.objects.get(pk=_a_object_id(id_producto))
    except inventory.Productos.DoesNotExist:
        return None


def _crear_factura_borrador(request, cliente, producto):
    """Crea la factura en BORRADOR con el primer ítem elegido."""
    cantidad = int(request.session.get('cantidad', 1))
    factura = models.Facturas()
    factura.cliente = _documento_cliente(cliente)
    factura.factura_detalle = [_nuevo_detalle(producto, cantidad)]
    factura.fecha = timezone.now()
    factura.save()
    producto.stock = producto.stock - cantidad
    producto.save()
    request.session.pop('id_producto', None)
    request.session.pop('cantidad', None)
    return factura


'''Crea elemento nuevo del inventario: añade el producto al carrito'''
def anadirItemInventario(request, id_producto):
    # Trae el producto seleccionado para añadir al carrito
    producto = _obtener_documento(inventory.Productos, id_producto)
    if request.method != 'POST':
        return redirect('inventario:productos_cliente')
    # Obtiene la cantidad enviada desde el formulario
    cantidad = int(request.POST.get('cantidad', 1))
    # Busca si hay una factura en modo borrador (el carrito)
    facturaActual = models.Facturas.objects.filter(estado='BORRADOR').first()
    if not facturaActual:
        # No hay carrito todavía: se guarda lo elegido en sesión y se pide el
        # cliente para poder crear la factura en borrador
        request.session['id_producto'] = str(producto.pk)
        request.session['cantidad'] = cantidad
        return redirect('billing:seleccionar_cliente')
    if cantidad < 1 or cantidad > producto.stock:
        messages.error(request, 'No hay suficientes unidades disponibles.')
        return redirect('inventario:productos_cliente')
    # Ya hay un carrito: el ítem se guarda embebido en la factura
    _agregar_detalle(facturaActual, _nuevo_detalle(producto, cantidad))
    _descontar_stock(producto, cantidad)
    messages.success(request, 'Producto añadido al carrito.')
    return redirect('inventario:productos_cliente')


'''Vista para seleccionar el cliente'''
def seleccionar_cliente(request):
    if request.method == 'POST':
        formulario = forms.CrearFacturaClienteForm(request.POST)
        if formulario.is_valid():
            # Obtiene el cliente seleccionado
            cliente = formulario.cleaned_data['cliente']
            request.session['cliente_id'] = str(cliente.pk)

            producto = _producto_de_sesion(request)
            if not producto:
                messages.error(
                    request,
                    'Selecciona un producto antes de crear la factura.'
                )
                return redirect('inventario:productos_cliente')
            _crear_factura_borrador(request, cliente, producto)
            messages.success(
                request,
                'Factura creada en borrador con el producto seleccionado.'
            )
            return redirect('inventario:productos_cliente')
        data = {
            'formulario': formulario,
            'mensaje': formulario.errors.as_text(),
            'titlePage': 'Seleccionar cliente'
        }
        return render(request, 'seleccionar_cliente.html', data)
    data = {
        'formulario': forms.CrearFacturaClienteForm(),
        'titlePage': 'Seleccionar cliente'
    }
    return render(request, 'seleccionar_cliente.html', data)


'''Muestra todos los elementos que se encuentran en el carrito'''
def mostrar_carrito(request):
    # Filtra si hay una factura en estado BORRADOR, si no hay ninguna se envía
    # un carrito vacío
    factura = _factura_borrador()
    if not factura:
        return render(
            request,
            'mostrar_carrito.html',
            {'detalles': [], 'total': 0, 'titlePage': 'Carrito'}
        )
    detalles = factura.factura_detalle or []
    total = sum(_campo(detalle, 'subtotal') for detalle in detalles)
    data = {'detalles': detalles, 'total': total, 'titlePage': 'Carrito'}
    return render(request, 'mostrar_carrito.html', data)


'''Cambia el estado de la compra a PAGADA y calcula el total de la factura'''
def finalizar_compra(request):
    factura = _factura_borrador()
    if not factura:
        messages.error(request, 'No hay ninguna factura en borrador.')
        return redirect('billing:mostrar_carrito')
    detalles = factura.factura_detalle or []
    total = sum(_campo(detalle, 'subtotal') for detalle in detalles)
    # El total del carrito ya incluye el IVA: se discrimina la base y el impuesto
    factura.iva = round(total * 0.19, 2)
    factura.subtotal = round(total - factura.iva, 2)
    factura.total = round(factura.subtotal + factura.iva, 2)
    factura.estado = models.Facturas.EstadosFactura.PAGADA
    factura.save()
    messages.success(request, 'Compra finalizada correctamente.')
    return redirect('billing:listar_facturas')


'''Muestra el listado de todas las facturas creadas'''
def listar_facturas(request):
    facturas = models.Facturas.objects.all()
    data = {'facturas': facturas, 'titlePage': 'Facturas'}
    return render(request, 'listado_facturas.html', data)


def _generar_pdf(html_content, filename):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    result_file = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=result_file)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    response.write(result_file.getvalue())
    return response


'''Vista que renderiza el PDF de la factura seleccionada'''
def generar_pdf_factura(request, id_factura):
    # Trae la factura y sus detalles para renderizarlos en el PDF
    factura = _obtener_documento(models.Facturas, id_factura)
    detalles = factura.factura_detalle or []
    html_content = render(
        request, 'pdf_factura.html', {'factura': factura, 'detalles': detalles}
    ).content.decode('utf-8')
    filename = f'factura_{factura.pk}.pdf'
    return _generar_pdf(html_content, filename)

