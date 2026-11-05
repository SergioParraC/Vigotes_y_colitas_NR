from djongo import models


class Categoria(models.Model):
    """Colección 'categorias'.

    Además de existir como colección propia (para el CRUD del módulo), se usa
    como contenedor del campo embebido ``Productos.categoria``, igual que en la
    versión relacional la categoría se relacionaba con el producto.
    """

    _id = models.ObjectIdField()
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la categoría')
    descripcion = models.CharField(
        max_length=250, blank=True, default='', verbose_name='Descripción'
    )

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    """Colección 'proveedores' y contenedor de ``Productos.proveedor``."""

    _id = models.ObjectIdField()
    nombre = models.CharField(max_length=100, verbose_name='Nombre del proveedor')
    contacto = models.CharField(max_length=100, verbose_name='Contacto')
    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    email = models.EmailField(verbose_name='Correo electrónico')
    direccion = models.CharField(
        max_length=70, blank=True, default='', verbose_name='Dirección'
    )

    class Meta:
        db_table = 'proveedores'

    def __str__(self):
        return self.nombre


class Productos(models.Model):
    """Colección 'productos'.

    Guarda una copia (desnormalizada) de la categoría y del proveedor dentro
    del propio documento, incluyendo su ``_id`` para conservar la referencia.
    """

    _id = models.ObjectIdField()
    nombre = models.CharField(max_length=100, verbose_name='Nombre del producto')
    categoria = models.EmbeddedField(model_container=Categoria)
    proveedor = models.EmbeddedField(model_container=Proveedor)
    descripcion = models.CharField(
        max_length=250, blank=True, default='', verbose_name='Descripción'
    )
    precio = models.FloatField(verbose_name='Precio unitario')
    stock = models.IntegerField(default=0, verbose_name='Cantidad disponible en stock')
    img = models.ImageField(
        upload_to='productos', blank=True, default='', verbose_name='Imagen del producto'
    )

    class Meta:
        db_table = 'productos'

    def __str__(self):
        return self.nombre
