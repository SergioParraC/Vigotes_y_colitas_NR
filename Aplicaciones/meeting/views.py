from datetime import datetime

from bson.errors import InvalidId
from bson.objectid import ObjectId
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from . import models
from ..customers import models as customers
from ..pets import forms as pets_forms

'''Vistas de citas: viven embebidas dentro de la mascota del cliente.'''

ESTADOS = dict(models.Citas.EstadosCita.choices)
TIPOS = dict(models.Citas.TiposCita.choices)


def _a_object_id(id_texto):
    """Convierte el identificador recibido por la URL al ObjectId de Mongo."""
    try:
        return ObjectId(str(id_texto))
    except (InvalidId, TypeError):
        raise Http404('El identificador del documento no es válido')


def _iterar_citas():
    """Recorre clientes y mascotas devolviendo (cliente, indice, mascota, posicion, cita)."""
    for cliente in customers.Cliente.objects.all():
        for indice, mascota in enumerate(cliente.mascotas or []):
            for posicion, cita in enumerate(mascota.get('citas') or []):
                yield cliente, indice, mascota, posicion, cita


def _buscar_cita(id_cita):
    """Busca una cita por su _id recorriendo clientes y mascotas."""
    identificador = _a_object_id(id_cita)
    for cliente, indice, mascota, posicion, cita in _iterar_citas():
        if cita.get('_id') == identificador:
            return cliente, indice, mascota, posicion, cita
    raise Http404('La cita solicitada no existe')


def _buscar_mascota(id_mascota):
    """Busca una mascota por su _id (para crearle una cita)."""
    identificador = _a_object_id(id_mascota)
    for cliente in customers.Cliente.objects.all():
        for indice, mascota in enumerate(cliente.mascotas or []):
            if mascota.get('_id') == identificador:
                return cliente, indice, mascota
    raise Http404('La mascota solicitada no existe')


def _guardar_mascota(cliente, indice, mascota):
    """Reescribe el arreglo de mascotas del cliente y guarda el documento."""
    lista = list(cliente.mascotas or [])
    lista[indice] = mascota
    cliente.mascotas = lista
    cliente.save()


def _fecha_hora(fecha_texto, hora_texto):
    """Combina la fecha y la hora del formulario en el DateTimeField."""
    try:
        fecha = datetime.strptime(fecha_texto, '%Y-%m-%d')
    except (TypeError, ValueError):
        fecha = datetime.now()
    if hora_texto:
        try:
            hora = datetime.strptime(hora_texto, '%H:%M').time()
            fecha = datetime.combine(fecha.date(), hora)
        except (TypeError, ValueError):
            pass
    return timezone.make_aware(fecha)


def _hora(hora_texto):
    """Convierte el texto de la hora en un ``time`` (o None si viene vacío)."""
    if not hora_texto:
        return None
    try:
        return datetime.strptime(hora_texto, '%H:%M').time()
    except (TypeError, ValueError):
        return None


def _datos_cita(datos):
    """Arma el subdocumento completo de la cita con los datos del POST."""
    return {
        '_id': ObjectId(),
        'tipo': datos.get('Tipo') or 'Consulta',
        'fecha': _fecha_hora(datos.get('FechaCita'), datos.get('HoraCita')),
        'hora_cita': _hora(datos.get('HoraCita')),
        'motivo': datos.get('Motivo') or '',
        'estado': datos.get('Estado') or 'PENDIENTE',
        'sintomas': datos.get('Sintomas') or '',
        'notas': datos.get('Notas') or '',
        'veterinario': datos.get('Veterinario') or '',
    }


def _actualizar_cita(cita, datos):
    """Copia los datos del POST sobre la cita existente."""
    cita['tipo'] = datos.get('Tipo') or cita.get('tipo')
    cita['fecha'] = _fecha_hora(datos.get('FechaCita'), datos.get('HoraCita'))
    cita['hora_cita'] = _hora(datos.get('HoraCita'))
    cita['motivo'] = datos.get('Motivo') or ''
    cita['estado'] = datos.get('Estado') or cita.get('estado')
    cita['sintomas'] = datos.get('Sintomas') or ''
    cita['notas'] = datos.get('Notas') or ''
    cita['veterinario'] = datos.get('Veterinario') or ''
    return cita


def _cita_para_plantilla(cliente, mascota, cita):
    """Datos planos de una cita para listados y formularios."""
    return {
        'id': cita.get('_id'),
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
        'sintomas': cita.get('sintomas'),
        'notas': cita.get('notas'),
        'motivo': cita.get('motivo'),
        'veterinario': cita.get('veterinario'),
    }


'''Listado de todas las citas'''
def home_citas(request):
    citas = []
    for cliente, indice, mascota, posicion, cita in _iterar_citas():
        citas.append(_cita_para_plantilla(cliente, mascota, cita))
    data = {
        'Citas': citas,
        'Total': len(citas),
        'titulo': 'Todas las Citas',
        'titlePage': 'Citas'
    }
    return render(request, 'citas-home.html', data)


'''Crear una cita para una mascota'''
def crear_cita(request):
    if request.method == 'POST':
        datos = request.POST
        id_cliente, id_mascota = pets_forms.separar_valor_mascota(
            datos.get('Mascota'))
        if not id_mascota:
            messages.error(request, 'Selecciona la mascota de la cita.')
            return redirect('citas:crear_cita')
        cliente, indice, mascota = _buscar_mascota(id_mascota)
        cita = _datos_cita(datos)
        citas = list(mascota.get('citas') or [])
        citas.append(cita)
        mascota['citas'] = citas
        _guardar_mascota(cliente, indice, mascota)
        messages.success(request, 'Cita creada correctamente.')
        return redirect('citas:detalle_cita', id_cita=cita['_id'])
    data = {
        'cita': None,
        'mascotas': pets_forms.opciones_mascotas(),
        'tipos': models.Citas.TiposCita.choices,
        'estados': models.Citas.EstadosCita.choices,
        'titulo': 'Crear Cita',
        'boton': 'Crear',
        'titlePage': 'Crear Cita'
    }
    return render(request, 'cita-detail.html', data)


'''Detalle y edición de una cita'''
def detalle_cita(request, id_cita):
    cliente, indice, mascota, posicion, cita = _buscar_cita(id_cita)
    if request.method == 'POST':
        _actualizar_cita(cita, request.POST)
        citas = list(mascota.get('citas') or [])
        citas[posicion] = cita
        mascota['citas'] = citas
        _guardar_mascota(cliente, indice, mascota)
        data = {
            'cita': _cita_para_plantilla(cliente, mascota, cita),
            'mascotas': pets_forms.opciones_mascotas(),
            'tipos': models.Citas.TiposCita.choices,
            'estados': models.Citas.EstadosCita.choices,
            'titulo': 'Editar Cita',
            'boton': 'Actualizar',
            'titlePage': 'Editar Cita',
            'mensaje': 'Cita editada exitosamente'
        }
        return render(request, 'cita-detail.html', data)
    data = {
        'cita': _cita_para_plantilla(cliente, mascota, cita),
        'mascotas': pets_forms.opciones_mascotas(),
        'tipos': models.Citas.TiposCita.choices,
        'estados': models.Citas.EstadosCita.choices,
        'titulo': 'Editar Cita',
        'boton': 'Actualizar',
        'titlePage': 'Editar Cita'
    }
    return render(request, 'cita-detail.html', data)


'''Formulario de búsqueda de citas'''
def buscar_cita(request):
    data = {
        'tipos': models.Citas.TiposCita.choices,
        'estados': models.Citas.EstadosCita.choices,
        'titlePage': 'Filtrar Citas'
    }
    return render(request, 'cita-search.html', data)


'''Filtra las citas por nombre de mascota, tipo y estado'''
def filtrar_citas(request):
    nombre = request.GET.get('nombre', '').strip().lower()
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')
    citas = []
    for cliente, indice, mascota, posicion, cita in _iterar_citas():
        if nombre and nombre not in (mascota.get('nombre') or '').lower():
            continue
        if tipo and cita.get('tipo') != tipo:
            continue
        if estado and cita.get('estado') != estado:
            continue
        citas.append(_cita_para_plantilla(cliente, mascota, cita))
    data = {
        'Citas': citas,
        'Total': len(citas),
        'titulo': 'Resultados de búsqueda',
        'titlePage': 'Citas'
    }
    return render(request, 'citas-home.html', data)


'''Eliminar una cita por su ID'''
def eliminar_cita(request, id_cita):
    try:
        cliente, indice, mascota, posicion, cita = _buscar_cita(id_cita)
        citas = list(mascota.get('citas') or [])
        citas.pop(posicion)
        mascota['citas'] = citas
        _guardar_mascota(cliente, indice, mascota)
        messages.success(request, 'Cita eliminada exitosamente.')
    except Http404:
        messages.error(request, 'La cita no existe o ya fue eliminada.')
    return redirect('citas:listado_citas')

