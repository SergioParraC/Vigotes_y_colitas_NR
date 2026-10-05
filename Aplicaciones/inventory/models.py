from djongo import models

class Categoria(models.Model):

    nombre = models.CharField(max_length=15)
    descripcion = models.CharField(max_length=50, null=True)
    class Meta:
        abstract = True

class Proveedor(models.Model):

    razonSocial = models.CharField(
        verbose_name=("Razon Social"), 
        max_length=50, 
        null=False
    )
    contacto = models.CharField(
        verbose_name="Persona de contacto", 
        max_length=25, 
        null=False
    )
    telefono = models.CharField(
        verbose_name="Número de contacto", 
        max_length=25, 
        null=False
    )
    email = models.EmailField(
        verbose_name="Persona de contacto", 
        null=True
    )
    dirección = models.CharField(
        verbose_name="Número de contacto", 
        max_length=20, 
        null=True
    )
    class Meta:
        abstract = True

class Productos(models.Model):

    nombre = models.CharField(
        verbose_name = 'Nombre del producto', 
        max_length=30, 
        null=False
    )
    categoria = models.EmbeddedField(model_container=Categoria)
    proveedor = models.EmbeddedField(model_container=Proveedor)
    descripcion = models.CharField(
        verbose_name = 'Descripción del producto', 
        max_length=100, 
        null=True
    )
    precio = models.DecimalField(
        verbose_name="Valor de venta",
        max_digits=10, 
        decimal_places=2,
    )
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        abstract = True