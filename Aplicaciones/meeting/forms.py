from datetime import datetime

from django import forms
from django.utils import timezone

from . import models
from ..pets import forms as pets_forms


class CitaForm(forms.Form):
    """Formulario validado para crear y actualizar citas embebidas."""

    mascota = forms.ChoiceField(label='Mascota y propietario', choices=())
    tipo = forms.ChoiceField(
        label='Tipo de cita', choices=models.Citas.TiposCita.choices)
    fecha = forms.DateField(
        label='Fecha', input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}))
    hora = forms.TimeField(
        label='Hora', input_formats=['%H:%M'],
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}))
    estado = forms.ChoiceField(
        label='Estado', choices=models.Citas.EstadosCita.choices,
        initial=models.Citas.EstadosCita.PENDIENTE)
    motivo = forms.CharField(
        label='Motivo de la cita', max_length=200, required=False)
    sintomas = forms.CharField(
        label='Síntomas', max_length=250, required=False,
        widget=forms.Textarea(attrs={'rows': 3}))
    notas = forms.CharField(
        label='Notas adicionales', max_length=250, required=False,
        widget=forms.Textarea(attrs={'rows': 3}))
    veterinario = forms.CharField(
        label='Veterinario asignado', max_length=100, required=False)

    def __init__(self, *args, opciones_mascotas=None, **kwargs):
        super().__init__(*args, **kwargs)
        if opciones_mascotas is None:
            opciones_mascotas = pets_forms.opciones_mascotas()
        self.fields['mascota'].choices = opciones_mascotas

    def documento(self, cita_id):
        """Construye el subdocumento que Djongo guarda dentro de la mascota."""
        fecha_hora = datetime.combine(
            self.cleaned_data['fecha'], self.cleaned_data['hora'])
        if timezone.is_naive(fecha_hora):
            fecha_hora = timezone.make_aware(
                fecha_hora, timezone.get_current_timezone())
        return {
            '_id': cita_id,
            'tipo': self.cleaned_data['tipo'],
            'fecha': fecha_hora,
            'hora_cita': self.cleaned_data['hora'],
            'motivo': self.cleaned_data.get('motivo') or '',
            'estado': self.cleaned_data['estado'],
            'sintomas': self.cleaned_data.get('sintomas') or '',
            'notas': self.cleaned_data.get('notas') or '',
            'veterinario': self.cleaned_data.get('veterinario') or '',
        }
