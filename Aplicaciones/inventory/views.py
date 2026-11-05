from django.shortcuts import render, redirect
from . import models
from django.contrib import messages
from django.http import Http404, HttpResponse
from bson.errors import InvalidId
from bson.objectid import ObjectId
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa
from . import forms
from ..billing import models as billing


def _a_object_id(id_texto):
    """Convierte el identificador recibido por la URL al ObjectId de MongoDB.

    Djongo no convierte el texto de la URL al ObjectId que usa como llave
    primaria, por eso la conversión se hace de forma explícita antes de
    consultar la colección.
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



# Se dejan comentarios en productos, ya que es la base para el resto de elementos

'''El carrito de compras vive en el módulo de facturación (Aplicaciones.billing)'''
def _obtener_cantidad_carrito():
    """Cuenta los ítems que hay en el carrito: la factura en estado BORRADOR."""
    factura = billing.Facturas.objects.filter(
        estado=billing.Facturas.EstadosFactura.BORRADOR
    ).first()
    if not factura:
        return 0
    return len(factura.factura_detalle or [])


'''Listado de categorias'''
def home_categorias(request):
    categorias = models.Categoria.objects.all()
    data = {
        'Categorias': categorias,
        'titlePage': "Crear categoría"
    }
    return render(request, 'categoria-home.html', data)

'''Crear una nueva categoria'''
def crear_categoria_formulario(request):
    if request.method == "POST":
        formulario = forms.CategoriaForm(request.POST)
        if formulario.is_valid():
            categoria = models.Categoria()
            categoria.nombre = formulario.cleaned_data["nombre"]
            categoria.descripcion = formulario.cleaned_data["descripcion"]
            categoria.save()
            messages.success(request, 'Categoría creada correctamente.')
            # El documento ya tiene su _id (ObjectId) generado por MongoDB
            return redirect('inventario:guardar_categoria', id_categoria=categoria.pk)
        data = {
            'formulario': formulario,
            'titulo': 'Crear categoría',
            'boton': 'Crear',
            'titlePage': 'Crear categoría',
            'mensaje': formulario.errors.as_text()
        }
        return render(request, 'categoria-detail.html', data)
    formulario = forms.CategoriaForm()
    data = {
        'formulario': formulario,
        'titulo': 'Crear categoría',
        'boton': 'Crear',
        'titlePage': 'Crear categoría'
    }
    return render(request, 'categoria-detail.html', data)

'''Editar categoria, usando el mismo template para crear'''
def guardar_categoria(request, id_categoria):
    categoria = _obtener_documento(models.Categoria, id_categoria)
    if request.method == "POST":
        formulario = forms.CategoriaForm(request.POST)
        if formulario.is_valid():
            categoria.nombre = formulario.cleaned_data["nombre"]
            categoria.descripcion = formulario.cleaned_data["descripcion"]
            categoria.save()

            data = {
                'categoria': categoria,
                'formulario': forms.CategoriaForm(initial={
                    'nombre': categoria.nombre,
                    'descripcion': categoria.descripcion
                }),
                'titulo': 'Editar categoría',
                'boton': 'Actualizar',
                'mensaje': 'Categoría actualizada correctamente.',
                'titlePage': 'Editar Categoría'
            }
            return render(request, 'categoria-detail.html', data)
        data = {
            'categoria': categoria,
            'formulario': formulario,
            'titulo': 'Editar categoría',
            'boton': 'Actualizar',
            'titlePage': 'Editar Categoría',
            'mensaje': formulario.errors.as_text()
        }
        return render(request, 'categoria-detail.html', data)
    else:
        formulario = forms.CategoriaForm(initial={
            'nombre': categoria.nombre,
            'descripcion': categoria.descripcion
        })
        data = {
            'categoria': categoria,
            'formulario': formulario,
            'titulo': 'Editar categoría',
            'boton': 'Actualizar',
            'titlePage': 'Editar Categoría'
        }
    return render(request, 'categoria-detail.html', data)

'''Listado de proveedores'''
def home_proveedores(request):
    proveedores = models.Proveedor.objects.all()
    total = proveedores.count()
    return render(request, 'proveedor-home.html', {
        'proveedores': proveedores,
        'total': total,
        'titlePage': 'Listado Proveedores'
    })

'''Crear un nuevo proveedor'''
def crear_proveedor_formulario(request):
    if request.method == "POST":
        formulario = forms.ProveedorForm(request.POST)
        if formulario.is_valid():
            proveedor = models.Proveedor()
            proveedor.nombre = formulario.cleaned_data["nombre"]
            proveedor.contacto = formulario.cleaned_data["contacto"]
            proveedor.telefono = formulario.cleaned_data["telefono"]
            proveedor.email = formulario.cleaned_data["email"]
            proveedor.direccion = formulario.cleaned_data["direccion"]
            proveedor.save()
            messages.success(request, 'Proveedor creado correctamente.')
            return redirect('inventario:guardar_proveedor', id_proveedor=proveedor.pk)
        data = {
            'formulario': formulario,
            'titulo': 'Crear proveedor',
            'boton_text': 'Crear',
            'titlePage': 'Crear proveedor',
            'mensaje': formulario.errors.as_text()
        }
        return render(request, 'proveedor-detail.html', data)
    formulario = forms.ProveedorForm()
    data = {
        'formulario': formulario,
        'titulo': 'Crear proveedor',
        'boton_text': 'Crear',
        'titlePage': 'Crear proveedor'
    }
    return render(request, 'proveedor-detail.html', data)

'''Eliminar un proveedor por ID'''
def eliminar_proveedor(request, id_proveedor):
    try:
        proveedor = _obtener_documento(models.Proveedor, id_proveedor)
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado exitosamente.')
    except Http404:
        messages.error(request, 'El proveedor no existe o ya fue eliminado.')
    return redirect('inventario:listado_proveedores')

'''Editar proveedor, usando el mismo template para crear'''
def guardar_proveedor(request, id_proveedor):
    proveedor = _obtener_documento(models.Proveedor, id_proveedor)
    if request.method == "POST":
        formulario = forms.ProveedorForm(request.POST)
        if formulario.is_valid():
            proveedor.nombre = formulario.cleaned_data["nombre"]
            proveedor.contacto = formulario.cleaned_data["contacto"]
            proveedor.telefono = formulario.cleaned_data["telefono"]
            proveedor.email = formulario.cleaned_data["email"]
            proveedor.direccion = formulario.cleaned_data["direccion"]
            proveedor.save()
            data = {
                'proveedor': proveedor,
                'formulario': forms.ProveedorForm(initial={
                    'nombre': proveedor.nombre,
                    'contacto': proveedor.contacto,
                    'telefono': proveedor.telefono,
                    'email': proveedor.email,
                    'direccion': proveedor.direccion
                }),
                'titulo': 'Editar proveedor',
                'boton_text': 'Actualizar',
                'mensaje': 'El proveedor se ha actualizado correctamente',
                'titlePage': 'Editar proveedor'
            }
            return render(request, 'proveedor-detail.html', data)
        data = {
            'formulario': formulario,
            'proveedor': proveedor,
            'titulo': 'Editar proveedor',
            'boton_text': 'Actualizar',
            'titlePage': 'Editar proveedor',
            'mensaje': formulario.errors.as_text()
        }
        return render(request, 'proveedor-detail.html', data)
    else:
        formulario = forms.ProveedorForm(initial={
            'nombre': proveedor.nombre,
            'contacto': proveedor.contacto,
            'telefono': proveedor.telefono,
            'email': proveedor.email,
            'direccion': proveedor.direccion
        })
        data = {
            'formulario': formulario,
            'proveedor': proveedor,
            'titulo': 'Editar proveedor',
            'boton_text': 'Actualizar',
            'titlePage': 'Editar proveedor'
        }
    return render(request, 'proveedor-detail.html', data)

'''Listado de productos'''
def home_producto(request):
    # Trae todos los productos, y un totalizador
    dataProductos = models.Productos.objects.all()
    dataTotal = models.Productos.objects.count()
    # Se envia el formulario de filtro
    data = {
        'formulario': forms.BuscarProductosForm(),
        'Productos': dataProductos,
        'Total': dataTotal,
        'titulo': 'Todos los productos',
        'titlePage': 'Productos',
        'origen_filtro': 'inventario'
    }
    return render(request, 'inventory-home.html', data)


def productos_cliente(request):
    cant_elementos_carrito = _obtener_cantidad_carrito()

    productos = models.Productos.objects.all()
    total = productos.count()
    data = {
        'formulario': forms.BuscarProductosForm(),
        'Productos': productos,
        'Total': total,
        'titulo': 'Catalogo de productos',
        'titlePage': 'Catalogo cliente',
        'cant_elementos_carrito': cant_elementos_carrito,
        'origen_filtro': 'cliente'
    }
    return render(request, 'productos_cliente.html', data)


def detalle_producto_cliente(request, id_producto):
    cant_elementos_carrito = _obtener_cantidad_carrito()
    producto = _obtener_documento(models.Productos, id_producto)
    data = {
        'producto': producto,
        'titulo': producto.nombre,
        'titlePage': f'Detalle | {producto.nombre}',
        'cant_elementos_carrito': cant_elementos_carrito
    }
    return render(request, 'productos-cliente-detail.html', data)

'''Crear un producto'''
def crear_producto_formulario(request):
    # Validación de formulario por POST
    if request.method == "POST":
        formulario = forms.ProductForm(request.POST, request.FILES)
        # Si el formulario es válido, se crea un nuevo producto con los datos del formulario y se guarda en la base de datos
        if formulario.is_valid():
            producto = models.Productos()
            producto.nombre = formulario.cleaned_data["nombre"]
            # La categoría y el proveedor se guardan embebidos en el documento del
            # producto, conservando el _id del documento al que hacen referencia
            categoria = formulario.cleaned_data["categoria"]
            producto.categoria = {
                '_id': categoria.pk,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion,
            }
            proveedor = formulario.cleaned_data["proveedor"]
            producto.proveedor = {
                '_id': proveedor.pk,
                'nombre': proveedor.nombre,
                'contacto': proveedor.contacto,
                'telefono': proveedor.telefono,
                'email': proveedor.email,
                'direccion': proveedor.direccion,
            }
            producto.descripcion = formulario.cleaned_data["descripcion"]
            producto.precio = formulario.cleaned_data["precio"]
            producto.stock = formulario.cleaned_data["cantidad_en_stock"]
            # Imagen es opcional
            if formulario.cleaned_data.get("imagen"):
                producto.img = formulario.cleaned_data["imagen"]
            producto.save()
            messages.success(request, 'Producto creado correctamente.')
            # Redirige a la pagina de edicion, por el ID
            return redirect('inventario:guardar_producto', id_producto=producto.pk)
        data = {
            'formulario': formulario,
            'producto': None,
            'boton': 'Crear',
            'titulo': 'Crear producto',
            'titlePage': 'Crear producto',
            'mensaje': formulario.errors.as_text()
        }
        return render(request, 'inventory-detail.html', data)
    else:
        formulario = forms.ProductForm()

    data = {
        'formulario': formulario,
        'producto': None,
        'boton': 'Crear',
        'titulo': 'Crear producto',
        'titlePage': 'Crear producto',
    }
    return render(request, 'inventory-detail.html', data)

'''Detalles de cada producto para editarlo'''
def guardar_producto(request, id_producto):
    # Se trae el producto por ID
    producto = _obtener_documento(models.Productos, id_producto)
    # En Mongo la categoría y el proveedor están embebidos como documentos
    categoria_id = producto.categoria.get('_id') if producto.categoria else None
    proveedor_id = producto.proveedor.get('_id') if producto.proveedor else None
    # Si se envia el formulario por POST, se valida y se actualiza el producto
    if request.method == "POST":
        formulario = forms.ProductForm(request.POST, request.FILES)
        if formulario.is_valid():
            producto.nombre = formulario.cleaned_data["nombre"]
            categoria = formulario.cleaned_data["categoria"]
            producto.categoria = {
                '_id': categoria.pk,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion,
            }
            proveedor = formulario.cleaned_data["proveedor"]
            producto.proveedor = {
                '_id': proveedor.pk,
                'nombre': proveedor.nombre,
                'contacto': proveedor.contacto,
                'telefono': proveedor.telefono,
                'email': proveedor.email,
                'direccion': proveedor.direccion,
            }
            producto.descripcion = formulario.cleaned_data["descripcion"]
            producto.precio = formulario.cleaned_data["precio"]
            producto.stock = formulario.cleaned_data["cantidad_en_stock"]
            if formulario.cleaned_data.get("imagen"):
                producto.img = formulario.cleaned_data["imagen"]
            producto.save()
            data = {
                'producto' : producto,
                'formulario': forms.ProductForm(initial={
                    'nombre': producto.nombre,
                    'categoria': categoria.pk,
                    'proveedor': proveedor.pk,
                    'descripcion': producto.descripcion,
                    'precio': producto.precio,
                    'cantidad_en_stock': producto.stock
                }),
                'boton' : 'Actualizar',
                'titulo' : 'Editar producto',
                'mensaje': 'Producto actualizado correctamente.',
                'titlePage': 'Editar producto'
             }
            return render(request, 'inventory-detail.html', data)
        # Si no es válido, se muestra el formulario con datos iniciales y con los errores
        data = {
            'producto': producto,
            'formulario': formulario,
            'boton': 'Actualizar',
            'titulo': 'Editar producto',
            'titlePage': 'Editar producto',
            'mensaje': formulario.errors.as_text()
        }
        return render(request, 'inventory-detail.html', data)
    # Si es otro método, se muestra el formulario con los datos del producto
    else:
        # Se carga el formulario con los datos del producto para mostrar en el template
        formulario = forms.ProductForm(initial={
            'nombre': producto.nombre,
            'categoria': categoria_id,
            'proveedor': proveedor_id,
            'descripcion': producto.descripcion,
            'precio': producto.precio,
            'cantidad_en_stock': producto.stock
        })
        # Se envia el producto para el id y el formulario
        data = {
            'producto': producto,
            'formulario': formulario,
            'boton': 'Actualizar',
            'titulo': 'Editar producto',
            'titlePage': 'Editar producto'
        }
    # Se renderiza el formuario según la data armada
    return render(request, 'inventory-detail.html', data)

'''Se pasan los filtros por POST, se filtran los productos'''
def filtrar_productos(request):
    # Se obtiene el formulario con los datos enviados por POST
    formulario = forms.BuscarProductosForm(request.POST)
    origen_filtro = request.POST.get('origen_filtro', 'inventario')
    # Se obtienen todos los productos para luego aplicar los filtros
    productos = models.Productos.objects.all()
    if formulario.is_valid():
        # Se obtienen los datos validados del formulario para aplicar los filtros correspondientes
        nombre = formulario.cleaned_data.get('nombre')
        categoria = formulario.cleaned_data.get('categoria')
        precio_min = formulario.cleaned_data.get('precio_minimo')
        precio_max = formulario.cleaned_data.get('precio_maximo')
        # Cada filtro no es obligatorio, se verifica
        if nombre:
            productos = productos.filter(nombre__icontains=nombre)
        if precio_min is not None:
            productos = productos.filter(precio__gte=float(precio_min))
        if precio_max is not None:
            productos = productos.filter(precio__lte=float(precio_max))
        if categoria:
            # La categoría está embebida en el documento del producto, por eso se
            # compara contra el nombre de la categoría elegida en el formulario
            productos = [
                producto for producto in productos
                if producto.categoria and producto.categoria.get('nombre') == categoria.nombre
            ]
    dataTotal = len(productos)
    data = {
        'formulario': formulario,
        'Productos': productos,
        'Total': dataTotal,
        'titulo': 'Resultados de búsqueda',
        'titlePage': 'Resultados de búsqueda',
        'origen_filtro': origen_filtro
    }
    # Valida de donde viene, si de la ventana de edición o de la ventana de clientes
    if origen_filtro == 'cliente':
        data['cant_elementos_carrito'] = _obtener_cantidad_carrito()
        return render(request, 'productos_cliente.html', data)
    data['volver_menu'] = True
    return render(request, 'inventory-home.html', data)

'''Eliminar un producto por ID'''
def eliminar_producto(request, id_producto):
    try:
        # Obtiene el producto por su ID y lo elimina
        producto = _obtener_documento(models.Productos, id_producto)
        producto.delete()
        # Manera de enviar mensajes de éxito o error al template usando el framework de mensajes de Django
        messages.success(request, 'Producto eliminado exitosamente.')
    except Http404:
        messages.error(request, 'El producto no existe o ya fue eliminado.')
    return redirect('inventario:listado_productos')


def _generar_pdf(html_content, filename):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    result_file = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=result_file)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    response.write(result_file.getvalue())
    return response


def generar_pdf_productos(request):
    productos = models.Productos.objects.all()
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
    cant_productos = productos.count()
    html_contend = render(request, 'pdf_export/pdf_productos.html', {'productos': productos, 'fecha': fecha, 'cant_productos': cant_productos}).content.decode('utf-8')
    return _generar_pdf(html_contend, 'productos.pdf')


def generar_pdf_proveedores(request):
    proveedores = models.Proveedor.objects.all()
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
    cant_proveedores = proveedores.count()
    html_contend = render(request, 'pdf_export/pdf_proveedores.html', {'proveedores': proveedores, 'fecha': fecha, 'cant_proveedores': cant_proveedores}).content.decode('utf-8')
    return _generar_pdf(html_contend, 'proveedores.pdf')

