from django.shortcuts import render

from . import forms


'''Página principal de la veterinaria'''
def home(request):
    data = {
        'titlePage': 'Veterinaria Vida Animal',
        'titulo': 'Veterinaria Vida Animal',
    }
    return render(request, 'home.html', data)


'''Formulario de contacto: guarda el mensaje y confirma el envío'''
def contacto(request):
    mensaje_contacto = ''

    if request.method == 'POST':
        formulario_contacto = forms.ContactoForm(request.POST)
        if formulario_contacto.is_valid():
            formulario_contacto.save()
            mensaje_contacto = 'Tu mensaje fue enviado correctamente.'
            # Se limpia el formulario para que no queden los datos enviados
            formulario_contacto = forms.ContactoForm()
    else:
        formulario_contacto = forms.ContactoForm()

    data = {
        'titlePage': 'Contacto',
        'titulo': 'Contacto',
        'formulario_contacto': formulario_contacto,
        'mensaje_contacto': mensaje_contacto,
    }
    return render(request, 'contacto.html', data)

