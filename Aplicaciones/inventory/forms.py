from bson.errors import InvalidId
from bson.objectid import ObjectId
from django import forms
from . import models


class ObjectIdModelChoiceField(forms.ModelChoiceField):
    """
    Esta clase gestiona la elección de la categoría o de proveedor
    dentro de los desplegables de los formularios, de acuerdo a 
    la información suminstrada en la conmsulta
    """

    def to_python(self, value):
        if value not in self.empty_values:
            try:
                value = ObjectId(value)
            except (InvalidId, TypeError):
                pass
        return super().to_python(value)


class ProductForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del producto'})
    )
    categoria = ObjectIdModelChoiceField(
        label="Categoría",
        queryset=models.Categoria.objects.all(),
        empty_label="Selecciona una categoría"
    )
    proveedor = ObjectIdModelChoiceField(
        queryset=models.Proveedor.objects.all(),
        empty_label="Selecciona un proveedor"
    )
    descripcion = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={'placeholder': 'Realiza una descripción del producto'})
    )
    precio = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 100'})
    )
    cantidad_en_stock = forms.IntegerField(
        min_value=0,
        max_value=200
    )
    imagen = forms.ImageField(required=False)


class BuscarProductosForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del producto'})
    )
    categoria = ObjectIdModelChoiceField(
        label="Categoría",
        queryset=models.Categoria.objects.all(),
        empty_label="Todas",
        required=False
    )
    precio_minimo = forms.DecimalField(
        label="Precio mínimo",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 100'})
    )
    precio_maximo = forms.DecimalField(
        label="Precio máximo",
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Ej: 800'})
    )


class ProveedorForm(forms.Form):
    nombre = forms.CharField(
        label="Empresa proveedora",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del proveedor'})
    )
    contacto = forms.CharField(
        label="Persona de contacto",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Persona de contacto'})
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=10,
        widget=forms.TextInput(attrs={'placeholder': 'Número de teléfono'})
    )
    email = forms.EmailField(
        max_length=50,
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'})
    )
    direccion = forms.CharField(
        label="Dirección",
        max_length=70,
        widget=forms.Textarea(attrs={'placeholder': 'Dirección del proveedor'})
    )


class CategoriaForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre de la categoría",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de la categoría'})
    )
    descripcion = forms.CharField(
        label="Descripción",
        max_length=250,
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Descripción de la categoría'})
    )
