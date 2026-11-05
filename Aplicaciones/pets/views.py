from datetime import date

from django.http import Http404
from django.shortcuts import redirect, render

from . import forms
from ..customers import models as customers

'''Vistas de mascotas: viven embebidas dentro del documento del cliente.'''


def calcular_edad(fecha_nacimiento):
    """Edad en años a partir de la fecha de nacimiento (igual que el origen)."""
    if not fecha_nacimiento:
        return 0
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


'''Listado de mascotas y totales'''
def home_pets(request):
    clientes = customers.Cliente.objects.all()
    total_mascotas = 0
    total_citas = 0
    total_vacunas = 0
    total_historiales = 0
    registradas = []
    for cliente in clientes:
        for mascota in (cliente.mascotas or []):
            total_mascotas += 1
            total_citas += len(mascota.get('citas') or [])
            total_vacunas += len(mascota.get('vacunas') or [])
            total_historiales += len(mascota.get('historia_clinica') or [])
            registradas.append({
                'id': mascota.get('_id'),
                'nombre': mascota.get('nombre'),
                'especie': mascota.get('especie'),
                'raza': mascota.get('raza'),
                'edad': calcular_edad(mascota.get('fecha_nacimiento')),
                'vacunado': mascota.get('vacunado'),
                'cliente': f'{cliente.nombre} {cliente.apellido}',
            })
    data = {
        'titlePage': 'Mascotas',
        'titulo': 'Gestión de mascotas',
        'total_duenos': len(clientes),
        'total_mascotas': total_mascotas,
        'total_citas': total_citas,
        'total_vacunas': total_vacunas,
        'total_historiales': total_historiales,
        'mascotas': registradas[:10],
    }
    return render(request, 'pets-home.html', data)


'''Registrar un dueño (cliente) y su mascota en un solo formulario'''
def registrar_mascota(request):
    if request.method == 'POST':
        formulario_dueno = forms.DuenoForm(request.POST)
        formulario_mascota = forms.MascotaForm(request.POST)
        if formulario_dueno.is_valid() and formulario_mascota.is_valid():
            dueno = formulario_dueno.save()
            mascota = formulario_mascota.save()
            dueno.mascotas = [mascota]
            dueno.save()
            return redirect('/pets/')
    else:
        formulario_dueno = forms.DuenoForm()
        formulario_mascota = forms.MascotaForm()
    data = {
        'titlePage': 'Registrar dueño y mascota',
        'titulo': 'Registrar dueño y mascota',
        'formulario_dueno': formulario_dueno,
        'formulario_mascota': formulario_mascota,
        'boton': 'Guardar registro',
        'url_cancelar': '/pets/',
    }
    return render(request, 'pets-mascota-form.html', data)


'''Editar el dueño (cliente) y la mascota en el mismo formulario'''
def editar_mascota(request, id_mascota):
    cliente = None
    indice = None
    mascota = None
    for actual in customers.Cliente.objects.all():
        for posicion, documento in enumerate(actual.mascotas or []):
            if str(documento.get('_id')) == str(id_mascota):
                cliente, indice, mascota = actual, posicion, documento
                break
        if mascota:
            break
    if mascota is None:
        raise Http404('La mascota solicitada no existe')

    if request.method == 'POST':
        formulario_dueno = forms.DuenoForm(request.POST, instance=cliente)
        formulario_mascota = forms.MascotaForm(request.POST, instance=mascota)
        if formulario_dueno.is_valid() and formulario_mascota.is_valid():
            formulario_dueno.save()
            mascota = formulario_mascota.save()
            lista = list(cliente.mascotas or [])
            lista[indice] = mascota
            cliente.mascotas = lista
            cliente.save()
            return redirect(f'/pets/mascotas/{mascota["_id"]}/historia/')
    else:
        formulario_dueno = forms.DuenoForm(instance=cliente)
        formulario_mascota = forms.MascotaForm(instance=mascota)

    data = {
        'titlePage': 'Editar dueño y mascota',
        'titulo': 'Editar dueño y mascota',
        'formulario_dueno': formulario_dueno,
        'formulario_mascota': formulario_mascota,
        'boton': 'Actualizar registro',
        'url_cancelar': f'/pets/mascotas/{mascota["_id"]}/historia/',
    }
    return render(request, 'pets-mascota-form.html', data)


'''Historia clínica de una mascota: citas, vacunas e historial médico'''
def historia_mascota(request, id_mascota):
    cliente = None
    mascota = None
    for actual in customers.Cliente.objects.all():
        for documento in (actual.mascotas or []):
            if str(documento.get('_id')) == str(id_mascota):
                cliente, mascota = actual, documento
                break
        if mascota:
            break
    if mascota is None:
        raise Http404('La mascota solicitada no existe')

    data = {
        'titlePage': f"Historia de {mascota.get('nombre')}",
        'titulo': f"Historia de {mascota.get('nombre')}",
        'mascota': dict(mascota, id=mascota.get('_id')),
        'cliente': cliente,
        'edad': calcular_edad(mascota.get('fecha_nacimiento')),
        'citas': mascota.get('citas') or [],
        'vacunas': [
            dict(vacuna, id=vacuna.get('_id'))
            for vacuna in (mascota.get('vacunas') or [])
        ],
        'historiales': [
            dict(historial, id=historial.get('_id'))
            for historial in (mascota.get('historia_clinica') or [])
        ],
    }
    return render(request, 'pets-historia.html', data)


'''Registrar una vacuna en la mascota elegida'''
def registrar_vacuna(request):
    if request.method == 'POST':
        formulario = forms.VacunaForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('/pets/')
    else:
        formulario = forms.VacunaForm()
    data = {
        'titlePage': 'Registrar vacuna',
        'titulo': 'Registrar vacuna',
        'formulario': formulario,
        'boton': 'Guardar vacuna',
        'url_cancelar': '/pets/',
    }
    return render(request, 'pets-form.html', data)


'''Editar una vacuna de la historia de la mascota'''
def editar_vacuna(request, id_vacuna):
    vacuna = None
    mascota = None
    for cliente in customers.Cliente.objects.all():
        for documento in (cliente.mascotas or []):
            for item in (documento.get('vacunas') or []):
                if str(item.get('_id')) == str(id_vacuna):
                    mascota = documento
                    vacuna = item
                    break
            if vacuna:
                break
        if vacuna:
            break
    if vacuna is None:
        raise Http404('La vacuna solicitada no existe')

    if request.method == 'POST':
        formulario = forms.VacunaForm(request.POST, instance=vacuna)
        if formulario.is_valid():
            formulario.save()
            return redirect(f'/pets/mascotas/{mascota["_id"]}/historia/')
    else:
        formulario = forms.VacunaForm(instance=vacuna)

    data = {
        'titlePage': 'Editar vacuna',
        'titulo': 'Editar vacuna',
        'formulario': formulario,
        'boton': 'Actualizar vacuna',
        'url_cancelar': f'/pets/mascotas/{mascota["_id"]}/historia/',
    }
    return render(request, 'pets-form.html', data)


'''Registrar un historial médico en la mascota elegida'''
def registrar_historial(request):
    if request.method == 'POST':
        formulario = forms.HistorialMedicoForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('/pets/')
    else:
        formulario = forms.HistorialMedicoForm()
    data = {
        'titlePage': 'Registrar historial médico',
        'titulo': 'Registrar historial médico',
        'formulario': formulario,
        'boton': 'Guardar historial',
        'url_cancelar': '/pets/',
    }
    return render(request, 'pets-form.html', data)


'''Editar un historial médico de la mascota'''
def editar_historial(request, id_historial):
    historial = None
    mascota = None
    for cliente in customers.Cliente.objects.all():
        for documento in (cliente.mascotas or []):
            for item in (documento.get('historia_clinica') or []):
                if str(item.get('_id')) == str(id_historial):
                    mascota = documento
                    historial = item
                    break
            if historial:
                break
        if historial:
            break
    if historial is None:
        raise Http404('El historial solicitado no existe')

    if request.method == 'POST':
        formulario = forms.HistorialMedicoForm(
            request.POST, instance=historial)
        if formulario.is_valid():
            formulario.save()
            return redirect(f'/pets/mascotas/{mascota["_id"]}/historia/')
    else:
        formulario = forms.HistorialMedicoForm(instance=historial)

    data = {
        'titlePage': 'Editar historial médico',
        'titulo': 'Editar historial médico',
        'formulario': formulario,
        'boton': 'Actualizar historial',
        'url_cancelar': f'/pets/mascotas/{mascota["_id"]}/historia/',
    }
    return render(request, 'pets-form.html', data)



