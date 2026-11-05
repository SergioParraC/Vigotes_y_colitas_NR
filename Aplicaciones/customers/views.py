from django.shortcuts import render

from . import forms
from . import models as customers
from ..billing import models as billing
from ..inventory import models as inventory


def home(request):
    clientes = list(customers.Cliente.objects.all())
    total_mascotas = sum(len(cliente.mascotas or []) for cliente in clientes)
    total_citas = sum(
        len(mascota.get('citas') or [])
        for cliente in clientes
        for mascota in (cliente.mascotas or [])
    )
    return render(request, 'home.html', {
        'titlePage': 'Veterinaria Vida Animal',
        'titulo': 'Veterinaria Vida Animal',
        'total_clientes': len(clientes),
        'total_mascotas': total_mascotas,
        'total_citas': total_citas,
        'total_productos': inventory.Productos.objects.count(),
        'total_facturas': billing.Facturas.objects.count(),
    })


def contacto(request):
    mensaje_contacto = ''
    if request.method == 'POST':
        formulario_contacto = forms.ContactoForm(request.POST)
        if formulario_contacto.is_valid():
            formulario_contacto.save()
            mensaje_contacto = 'Tu mensaje fue enviado correctamente.'
            formulario_contacto = forms.ContactoForm()
    else:
        formulario_contacto = forms.ContactoForm()
    return render(request, 'contacto.html', {
        'titlePage': 'Contacto', 'titulo': 'Contacto',
        'formulario_contacto': formulario_contacto,
        'mensaje_contacto': mensaje_contacto,
    })
