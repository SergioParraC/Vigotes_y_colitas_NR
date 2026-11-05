from io import BytesIO

from bson.errors import InvalidId
from bson.objectid import ObjectId
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from xhtml2pdf import pisa

from . import forms, models
from ..inventory import models as inventory

'''Vistas para el proceso de facturación, incluyendo selección de cliente, selección de mascota, añadir productos al carrito y mostrar el carrito de compras.'''


'''Crea elemento nuevo del inventario: añade el producto al carrito'''
def anadirItemInventario(request, id_producto):
    # Trae el producto seleccionado para añadir al carrito
    try:
        producto = inventory.Productos.objects.get(
            pk=ObjectId(str(id_producto)))
    except (InvalidId, TypeError):
        raise Http404('El identificador del documento no es válido')
    except inventory.Productos.DoesNotExist:
        raise Http404('El producto solicitado no existe')

    if request.method == 'POST':
        # Obitiene la cantidad
        cantidad = int(request.POST.get('cantidad', 1))
        # Buscar si hay una factura en modo borrador
        facturaActual = models.Facturas.objects.filter(
            estado='BORRADOR').first()
        try:
            # Si no hay factura en modo borrador, redirige a seleccionar
            # cliente para crear una nueva factura
            if not facturaActual:
                # Métodos en donde se guardan elementos en sesión, y se usarán
                # más adelante después de seleccionar cliente y mascota
                request.session['id_producto'] = str(producto.pk)
                request.session['cantidad'] = cantidad
                return redirect('billing:seleccionar_cliente')
            else:
                # Ya hay una factura en modo borrador, se añade el producto
                # seleccionado a esa factura
                detalles = list(facturaActual.factura_detalle or [])
                detalles.append(
                    forms.detalle_de_producto(producto, cantidad))
                # Los ítems van embebidos: se reescribe el arreglo completo
                facturaActual.factura_detalle = detalles
                facturaActual.save()
                # Disminuye la cantidad de lementos para el producto en cuestion
                producto.stock = producto.stock - cantidad
                producto.save()
                # Valida si se añadió desde la página principal o desde
                # detalles, y redirige
                return redirect('inventario:productos_cliente')
        # Si ocurre un error, redirige
        except Exception as e:
            return redirect('inventario:productos_cliente')
    return redirect('inventario:productos_cliente')


'''Vista para seleccionar el cliente'''
def seleccionar_cliente(request):
    if request.method == 'POST':
        # Renderiza el formulario para seleccionar primero el cliente
        formulario = forms.CrearFacturaClienteForm(request.POST)
        if formulario.is_valid():
            # Obtiene el cliente seleccionado
            clienteSeleccionado = formulario.cleaned_data['cliente']
            # Guarda el cliente seleccionado en la sesión para usarlo más
            # adelante en el proceso de facturación
            request.session['cliente_id'] = str(clienteSeleccionado.pk)
            return redirect('billing:seleccionar_mascota')
        return render(
            request, 'seleccionar_cliente.html', {'formulario': formulario})
    return render(
        request,
        'seleccionar_cliente.html',
        {'formulario': forms.CrearFacturaClienteForm()}
    )


'''Vista para seleccionar la mascota, después de seleccionar el cliente'''
def seleccionar_mascota(request):
    # Obtiene los datos guardados en la sesión
    cliente_id = request.session.get('cliente_id')
    id_producto = request.session.get('id_producto')
    # Trae el producto seleccionado para añadir al carrito
    try:
        producto = inventory.Productos.objects.get(
            pk=ObjectId(str(id_producto)))
    except (InvalidId, TypeError):
        raise Http404('El identificador del documento no es válido')
    except inventory.Productos.DoesNotExist:
        raise Http404('El producto solicitado no existe')

    if request.method == 'POST':
        # Obtiene la cantidad desde la sesión, si no hay se asigna 1
        cantidad = int(request.session.get('cantidad', 1))
        # Trae la respuesta del formulario
        formulario = forms.CrearFacturaMascotaForm(
            request.POST, cliente_id=cliente_id,
            producto=producto, cantidad=cantidad)
        if formulario.is_valid():
            # Crea la factura en estado BORRADOR con el cliente, la mascota
            # seleccionada y el primer ítem del carrito
            formulario.save()
            # Disminuye la cantidad de elementos para el producto en cuestión
            producto.stock = producto.stock - cantidad
            producto.save()
            # Limpia los datos de la compra que quedaron en la sesión
            request.session.pop('id_producto', None)
            request.session.pop('cantidad', None)
            # Redirige a la página principal del catálogo
            return redirect('inventario:productos_cliente')
        # Si el formulario no es válido, vuelve a mostrarlo con errores
        return render(
            request, 'seleccionar_mascota.html', {'formulario': formulario})
    else:
        # Cuando el método es GET se muestran las mascotas del cliente
        formulario = forms.CrearFacturaMascotaForm(cliente_id=cliente_id)
        return render(
            request, 'seleccionar_mascota.html', {'formulario': formulario})


'''Muestra todos los elementos que se encuentran en el carrito'''
def mostrar_carrito(request):
    # Filtra si hay una factura en estado BORRADOR, si no hay ninguna se
    # envía un carrito vacío
    factura = models.Facturas.objects.filter(estado='BORRADOR').first()
    if not factura:
        return render(request, 'mostrar_carrito.html', {
            'detalles': [], 'total': 0, 'titlePage': 'Carrito'})
    detalles = factura.factura_detalle or []
    total = sum(detalle.get('subtotal') for detalle in detalles)
    return render(request, 'mostrar_carrito.html', {
        'detalles': detalles, 'total': total, 'titlePage': 'Carrito'})


'''Cambia el estado de la compra a PAGADA, y calcula el total de la factura'''
def finalizar_compra(request):
    factura = models.Facturas.objects.filter(estado='BORRADOR').first()
    if factura:
        detalles = factura.factura_detalle or []
        total = sum(detalle.get('subtotal') for detalle in detalles)
        factura.subtotal = round(total * 0.81, 2)   # Subtotal sin IVA
        factura.iva = round(total * 0.19, 2)        # IVA del 19%
        factura.total = round(factura.subtotal + factura.iva, 2)
        factura.estado = 'PAGADA'
        factura.save()
    return redirect('billing:listar_facturas')


'''Muestra el listado de todas las facturas creadas'''
def listar_facturas(request):
    facturas = models.Facturas.objects.all()
    data = {'facturas': facturas, 'titlePage': 'Facturas'}
    return render(request, 'listado_facturas.html', data)


'''Genera un PDF con los detalles de la factura'''
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
    try:
        factura = models.Facturas.objects.get(pk=ObjectId(str(id_factura)))
    except (InvalidId, TypeError):
        raise Http404('El identificador del documento no es válido')
    except models.Facturas.DoesNotExist:
        raise Http404('La factura solicitada no existe')
    detalles = factura.factura_detalle or []
    # Envía los datos de la factura y la plantilla HTML para renderizar
    html_content = render(
        request, 'pdf_factura.html', {'factura': factura, 'detalles': detalles}
    ).content.decode('utf-8')
    filename = f'factura_{factura.pk}.pdf'
    return _generar_pdf(html_content, filename)

