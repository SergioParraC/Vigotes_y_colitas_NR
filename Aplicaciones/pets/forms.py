from bson.objectid import ObjectId
from django import forms
from django.http import Http404

from ..customers.models import Cliente


def opciones_mascotas():
    """Opciones (valor, texto) con todas las mascotas de todos los clientes.

    En Mongo las mascotas viven embebidas en el cliente, así que el valor del
    ``ChoiceField`` lleva el cliente y el ``_id`` de la mascota juntos.
    """
    opciones = []
    for cliente in Cliente.objects.all():
        for mascota in (cliente.mascotas or []):
            valor = f"{cliente.pk}:{mascota.get('_id')}"
            texto = f"{mascota.get('nombre')} ({cliente.nombre} {cliente.apellido})"
            opciones.append((valor, texto))
    return opciones


def separar_valor_mascota(valor):
    """Separa el valor ``cliente:_id`` que devuelve el desplegable."""
    if not valor or ':' not in valor:
        return None, None
    id_cliente, id_mascota = valor.split(':', 1)
    return id_cliente, id_mascota


def mascota_de_registro(identificador, campo):
    """Valor ``cliente:_id`` de la mascota que contiene el registro."""
    for cliente in Cliente.objects.all():
        for mascota in (cliente.mascotas or []):
            for actual in (mascota.get(campo) or []):
                if str(actual.get('_id')) == str(identificador):
                    return f"{cliente.pk}:{mascota.get('_id')}"
    return ''


class DuenoForm(forms.Form):
    """Datos del dueño (cliente) al registrar dueño y mascota juntos."""

    nombre = forms.CharField(label="Nombres del dueño", max_length=15)
    apellido = forms.CharField(label="Apellidos del dueño", max_length=15)
    tipo_documento = forms.ChoiceField(
        label="Tipo de documento",
        choices=Cliente.TipoDocumento.choices
    )
    numero_documeto = forms.CharField(
        label="Número de documento", max_length=15)
    telefono = forms.CharField(label="Teléfono", max_length=25)
    email = forms.EmailField(label="Correo electrónico", max_length=50)
    direccion = forms.CharField(
        label="Dirección", max_length=200, required=False)

    def __init__(self, *args, instance=None, **kwargs):
        # El dueño y la mascota tienen un campo "nombre" cada uno, así que
        # cada formulario lleva su prefijo para que el POST no los mezcle.
        kwargs.setdefault('prefix', 'dueno')
        self.instance = instance
        initial = kwargs.get('initial', {})
        if instance:
            initial.update({
                'nombre': instance.nombre,
                'apellido': instance.apellido,
                'tipo_documento': instance.tipo_documento,
                'numero_documeto': instance.numero_documeto,
                'telefono': instance.telefono,
                'email': instance.email,
                'direccion': instance.direccion,
            })
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self):
        dueno = self.instance or Cliente()
        dueno.nombre = self.cleaned_data['nombre']
        dueno.apellido = self.cleaned_data['apellido']
        dueno.tipo_documento = self.cleaned_data['tipo_documento']
        dueno.numero_documeto = self.cleaned_data['numero_documeto']
        dueno.email = self.cleaned_data['email']
        dueno.telefono = self.cleaned_data['telefono']
        dueno.direccion = self.cleaned_data['direccion']
        if self.instance is None:
            # djongo exige el documento del cliente completo
            dueno.mascotas = []
        dueno.save()
        return dueno


class MascotaForm(forms.Form):
    """Datos de la mascota, iguales a los del proyecto de origen."""

    nombre = forms.CharField(label="Nombre de la mascota", max_length=50)
    especie = forms.CharField(label="Especie", max_length=50)
    raza = forms.CharField(label="Raza", max_length=50, required=False)
    fecha_nacimiento = forms.DateField(
        label="Fecha de nacimiento",
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})
    )
    peso = forms.FloatField(
        label="Peso",
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    vacunado = forms.BooleanField(label="Vacunado", required=False)

    def __init__(self, *args, instance=None, **kwargs):
        kwargs.setdefault('prefix', 'mascota')
        self.instance = instance
        initial = kwargs.get('initial', {})
        if instance:
            initial.update({
                'nombre': instance.get('nombre'),
                'especie': instance.get('especie'),
                'raza': instance.get('raza'),
                'fecha_nacimiento': instance.get('fecha_nacimiento'),
                'peso': instance.get('peso'),
                'vacunado': instance.get('vacunado'),
            })
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self):
        """Devuelve el subdocumento de la mascota (lo guarda la vista)."""
        mascota = self.instance or {
            '_id': ObjectId(),
            'historia_clinica': [],
            'vacunas': [],
            'citas': [],
        }
        mascota['nombre'] = self.cleaned_data['nombre']
        mascota['especie'] = self.cleaned_data['especie']
        mascota['raza'] = self.cleaned_data.get('raza') or ''
        mascota['fecha_nacimiento'] = self.cleaned_data.get(
            'fecha_nacimiento')
        mascota['peso'] = self.cleaned_data.get('peso') or 0
        mascota['vacunado'] = bool(self.cleaned_data.get('vacunado'))
        return mascota


class VacunaForm(forms.Form):
    """Datos de una vacuna (se usa para registrar y para editar)."""

    mascota = forms.ChoiceField(label="Mascota", choices=())
    nombre_vacuna = forms.CharField(label="Nombre de la vacuna", max_length=100)
    fecha_aplicacion = forms.DateField(
        label="Fecha de aplicación",
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})
    )
    veterinario = forms.CharField(label="Veterinario", max_length=100)

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        initial = kwargs.get('initial', {})
        if instance:
            initial.update({
                'mascota': mascota_de_registro(
                    instance.get('_id'), 'vacunas'),
                'nombre_vacuna': instance.get('nombre_vacuna'),
                'fecha_aplicacion': instance.get('fecha_aplicacion'),
                'veterinario': instance.get('veterinario'),
            })
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
        self.fields['mascota'].choices = opciones_mascotas()

    def save(self):
        """Crea o actualiza la vacuna dentro de la mascota elegida."""
        id_cliente, id_mascota = separar_valor_mascota(
            self.cleaned_data.get('mascota'))
        vacuna = {
            '_id': (self.instance or {}).get('_id') or ObjectId(),
            'nombre_vacuna': self.cleaned_data['nombre_vacuna'],
            'fecha_aplicacion': self.cleaned_data['fecha_aplicacion'],
            'veterinario': self.cleaned_data['veterinario'],
        }
        encontrada = False
        for cliente in Cliente.objects.all():
            lista = list(cliente.mascotas or [])
            cambio = False
            for indice, mascota in enumerate(lista):
                anteriores = mascota.get('vacunas') or []
                vacunas = [
                    actual for actual in anteriores
                    if str(actual.get('_id')) != str(vacuna['_id'])
                ]
                borrada = len(vacunas) != len(anteriores)
                es_destino = str(mascota.get('_id')) == str(id_mascota)
                if es_destino:
                    vacunas.append(vacuna)
                    encontrada = True
                if borrada or es_destino:
                    mascota['vacunas'] = vacunas
                    lista[indice] = mascota
                    cambio = True
            if cambio:
                cliente.mascotas = lista
                cliente.save()
        if not encontrada:
            raise Http404('La mascota solicitada no existe')
        return vacuna


class HistorialMedicoForm(forms.Form):
    """Datos de un historial médico (se usa para registrar y para editar)."""

    mascota = forms.ChoiceField(label="Mascota", choices=())
    alergias = forms.CharField(
        label="Alergias",
        max_length=250,
        required=False,
        widget=forms.Textarea
    )
    fecha_visita = forms.DateField(
        label="Fecha de visita",
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})
    )
    motivo_visita = forms.CharField(
        label="Motivo de visita", max_length=200)
    diagnostico = forms.CharField(
        label="Diagnóstico", max_length=250, widget=forms.Textarea)
    tratamiento = forms.CharField(
        label="Tratamiento", max_length=250, widget=forms.Textarea)

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        initial = kwargs.get('initial', {})
        if instance:
            initial.update({
                'mascota': mascota_de_registro(
                    instance.get('_id'), 'historia_clinica'),
                'alergias': instance.get('alergias'),
                'fecha_visita': instance.get('fecha_visita'),
                'motivo_visita': instance.get('motivo_visita'),
                'diagnostico': instance.get('diagnostico'),
                'tratamiento': instance.get('tratamiento'),
            })
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
        self.fields['mascota'].choices = opciones_mascotas()

    def save(self):
        """Crea o actualiza el historial dentro de la mascota elegida."""
        id_cliente, id_mascota = separar_valor_mascota(
            self.cleaned_data.get('mascota'))
        historial = {
            '_id': (self.instance or {}).get('_id') or ObjectId(),
            'alergias': self.cleaned_data.get('alergias') or '',
            'fecha_visita': self.cleaned_data['fecha_visita'],
            'motivo_visita': self.cleaned_data['motivo_visita'],
            'diagnostico': self.cleaned_data['diagnostico'],
            'tratamiento': self.cleaned_data['tratamiento'],
        }
        encontrada = False
        for cliente in Cliente.objects.all():
            lista = list(cliente.mascotas or [])
            cambio = False
            for indice, mascota in enumerate(lista):
                anteriores = mascota.get('historia_clinica') or []
                historiales = [
                    actual for actual in anteriores
                    if str(actual.get('_id')) != str(historial['_id'])
                ]
                borrado = len(historiales) != len(anteriores)
                es_destino = str(mascota.get('_id')) == str(id_mascota)
                if es_destino:
                    historiales.append(historial)
                    encontrada = True
                if borrado or es_destino:
                    mascota['historia_clinica'] = historiales
                    lista[indice] = mascota
                    cambio = True
            if cambio:
                cliente.mascotas = lista
                cliente.save()
        if not encontrada:
            raise Http404('La mascota solicitada no existe')
        return historial

