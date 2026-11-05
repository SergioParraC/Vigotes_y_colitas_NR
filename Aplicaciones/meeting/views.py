from datetime import datetime

from bson.errors import InvalidId
from bson.objectid import ObjectId
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from . import forms, models
from ..customers import models as customers
from ..pets import forms as pets_forms


ESTADOS = dict(models.Citas.EstadosCita.choices)
TIPOS = dict(models.Citas.TiposCita.choices)


def _a_object_id(id_texto):
    try:
        return ObjectId(str(id_texto))
    except (InvalidId, TypeError):
        raise Http404('El identificador del documento no es válido')


def _iterar_citas():
    """Recorre las citas embebidas en las mascotas de cada cliente."""
    for cliente in customers.Cliente.objects.all():
        for indice, mascota in enumerate(cliente.mascotas or []):
            for posicion, cita in enumerate(mascota.get('citas') or []):
                yield cliente, indice, mascota, posicion, cita


def _buscar_cita(id_cita):
    identificador = _a_object_id(id_cita)
    for cliente, indice, mascota, posicion, cita in _iterar_citas():
        if cita.get('_id') == identificador:
            return cliente, indice, mascota, posicion, cita
    raise Http404('La cita solicitada no existe')


def _buscar_mascota(id_cliente, id_mascota):
    """Valida que la mascota pertenezca al cliente enviado por el formulario."""
    cliente_id = _a_object_id(id_cliente)
    mascota_id = _a_object_id(id_mascota)
    try:
        cliente = customers.Cliente.objects.get(pk=cliente_id)
    except customers.Cliente.DoesNotExist:
        raise Http404('El propietario seleccionado no existe')
    for indice, mascota in enumerate(cliente.mascotas or []):
        if mascota.get('_id') == mascota_id:
            return cliente, indice, mascota
    raise Http404('La mascota seleccionada no pertenece al propietario')


def _mascota_desde_valor(valor):
    id_cliente, id_mascota = pets_forms.separar_valor_mascota(valor)
    if not id_cliente or not id_mascota:
        raise Http404('Selecciona una mascota válida')
    return _buscar_mascota(id_cliente, id_mascota)


def _guardar_mascota(cliente, indice, mascota):
    mascotas = list(cliente.mascotas or [])
    mascotas[indice] = mascota
    cliente.mascotas = mascotas
    cliente.save()


def _estado_clase(estado):
    return {
        models.Citas.EstadosCita.PENDIENTE: 'pendiente',
        models.Citas.EstadosCita.CONFIRMADA: 'confirmada',
        models.Citas.EstadosCita.COMPLETADA: 'completada',
        models.Citas.EstadosCita.CANCELADA: 'cancelada',
    }.get(estado, 'pendiente')


def _cita_para_plantilla(cliente, mascota, cita):
    return {
        'id': cita.get('_id'),
        'mascota_id': mascota.get('_id'),
        'mascota': mascota.get('nombre'),
        'valor_mascota': f"{cliente.pk}:{mascota.get('_id')}",
        'especie': mascota.get('especie'),
        'cliente': f'{cliente.nombre} {cliente.apellido}',
        'telefono': cliente.telefono,
        'email': cliente.email,
        'tipo': cita.get('tipo'),
        'tipo_display': TIPOS.get(cita.get('tipo'), cita.get('tipo')),
        'fecha_cita': cita.get('fecha'),
        'hora_cita': cita.get('hora_cita'),
        'estado': ESTADOS.get(cita.get('estado'), cita.get('estado')),
        'valor_estado': cita.get('estado'),
        'estado_clase': _estado_clase(cita.get('estado')),
        'sintomas': cita.get('sintomas') or '',
        'notas': cita.get('notas') or '',
        'motivo': cita.get('motivo') or '',
        'veterinario': cita.get('veterinario') or '',
    }


def _todas_las_citas():
    citas = [
        _cita_para_plantilla(cliente, mascota, cita)
        for cliente, _, mascota, _, cita in _iterar_citas()
    ]
    minimo = timezone.make_aware(
        datetime(1970, 1, 1), timezone.get_current_timezone())
    def fecha_orden(item):
        fecha = item.get('fecha_cita')
        if not fecha:
            return minimo
        if timezone.is_naive(fecha):
            return timezone.make_aware(fecha, timezone.get_current_timezone())
        return fecha
    citas.sort(
        key=fecha_orden,
        reverse=True,
    )
    return citas


def _estadisticas(citas):
    return {
        'total': len(citas),
        'pendientes': sum(c['valor_estado'] == 'PENDIENTE' for c in citas),
        'confirmadas': sum(c['valor_estado'] == 'CONFIRMADA' for c in citas),
        'completadas': sum(c['valor_estado'] == 'COMPLETADA' for c in citas),
    }


def _contexto_listado(citas, titulo='Agenda de citas', filtros=None):
    return {
        'Citas': citas,
        'Total': len(citas),
        'estadisticas': _estadisticas(citas),
        'tipos': models.Citas.TiposCita.choices,
        'estados': models.Citas.EstadosCita.choices,
        'filtros': filtros or {},
        'titulo': titulo,
        'titlePage': 'Citas',
    }


def home_citas(request):
    return render(
        request, 'citas-home.html', _contexto_listado(_todas_las_citas()))


def crear_cita(request):
    opciones = pets_forms.opciones_mascotas()
    inicial = {
        'estado': models.Citas.EstadosCita.PENDIENTE,
        'fecha': timezone.localdate(),
    }
    mascota_inicial = request.GET.get('mascota')
    if mascota_inicial:
        inicial['mascota'] = mascota_inicial
    formulario = forms.CitaForm(
        request.POST or None, initial=inicial, opciones_mascotas=opciones)
    if request.method == 'POST' and formulario.is_valid():
        cliente, indice, mascota = _mascota_desde_valor(
            formulario.cleaned_data['mascota'])
        cita = formulario.documento(ObjectId())
        citas = list(mascota.get('citas') or [])
        citas.append(cita)
        mascota['citas'] = citas
        _guardar_mascota(cliente, indice, mascota)
        messages.success(request, 'Cita creada correctamente.')
        return redirect('citas:detalle_cita', id_cita=cita['_id'])
    return render(request, 'cita-detail.html', {
        'formulario': formulario,
        'cita': None,
        'titulo': 'Agendar nueva cita',
        'boton': 'Guardar cita',
        'titlePage': 'Crear cita',
    })


def detalle_cita(request, id_cita):
    cliente, indice, mascota, posicion, cita = _buscar_cita(id_cita)
    cita_vista = _cita_para_plantilla(cliente, mascota, cita)
    inicial = {
        'mascota': cita_vista['valor_mascota'],
        'tipo': cita.get('tipo'),
        'fecha': cita.get('fecha'),
        'hora': cita.get('hora_cita'),
        'estado': cita.get('estado'),
        'motivo': cita.get('motivo'),
        'sintomas': cita.get('sintomas'),
        'notas': cita.get('notas'),
        'veterinario': cita.get('veterinario'),
    }
    formulario = forms.CitaForm(request.POST or None, initial=inicial)
    if request.method == 'POST' and formulario.is_valid():
        destino_cliente, _, destino_mascota = _mascota_desde_valor(
            formulario.cleaned_data['mascota'])
        cita_actualizada = formulario.documento(cita.get('_id'))
        mismo_destino = (
            str(destino_cliente.pk) == str(cliente.pk)
            and str(destino_mascota.get('_id')) == str(mascota.get('_id'))
        )
        if mismo_destino:
            citas = list(mascota.get('citas') or [])
            citas[posicion] = cita_actualizada
            mascota['citas'] = citas
            _guardar_mascota(cliente, indice, mascota)
        else:
            citas_origen = list(mascota.get('citas') or [])
            citas_origen.pop(posicion)
            mascota['citas'] = citas_origen
            _guardar_mascota(cliente, indice, mascota)

            # Se vuelve a consultar el destino para evitar guardar una copia
            # anterior si ambas mascotas tienen el mismo propietario.
            destino_cliente, destino_indice, destino_mascota = (
                _mascota_desde_valor(formulario.cleaned_data['mascota']))
            citas_destino = list(destino_mascota.get('citas') or [])
            citas_destino.append(cita_actualizada)
            destino_mascota['citas'] = citas_destino
            _guardar_mascota(destino_cliente, destino_indice, destino_mascota)
        messages.success(request, 'Cita actualizada correctamente.')
        return redirect('citas:detalle_cita', id_cita=cita_actualizada['_id'])
    return render(request, 'cita-detail.html', {
        'formulario': formulario,
        'cita': cita_vista,
        'titulo': 'Detalle de la cita',
        'boton': 'Guardar cambios',
        'titlePage': 'Detalle de cita',
    })


def buscar_cita(request):
    return render(request, 'cita-search.html', {
        'tipos': models.Citas.TiposCita.choices,
        'estados': models.Citas.EstadosCita.choices,
        'titlePage': 'Buscar citas',
    })


def filtrar_citas(request):
    filtros = {
        'nombre': request.GET.get('nombre', '').strip(),
        'tipo': request.GET.get('tipo', ''),
        'estado': request.GET.get('estado', ''),
    }
    nombre = filtros['nombre'].lower()
    citas = []
    for cita in _todas_las_citas():
        if nombre and nombre not in cita['mascota'].lower():
            continue
        if filtros['tipo'] and cita['tipo'] != filtros['tipo']:
            continue
        if filtros['estado'] and cita['valor_estado'] != filtros['estado']:
            continue
        citas.append(cita)
    return render(request, 'citas-home.html', _contexto_listado(
        citas, 'Resultados de búsqueda', filtros))


def eliminar_cita(request, id_cita):
    cliente, indice, mascota, posicion, cita = _buscar_cita(id_cita)
    cita_vista = _cita_para_plantilla(cliente, mascota, cita)
    if request.method == 'POST':
        citas = list(mascota.get('citas') or [])
        citas.pop(posicion)
        mascota['citas'] = citas
        _guardar_mascota(cliente, indice, mascota)
        messages.success(request, 'Cita eliminada correctamente.')
        return redirect('citas:listado_citas')
    return render(request, 'cita-delete.html', {
        'cita': cita_vista,
        'titlePage': 'Eliminar cita',
    })
