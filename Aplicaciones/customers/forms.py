from django import forms

from . import models


'''Formulario para recibir los mensajes de contacto de la página principal'''
class ContactoForm(forms.ModelForm):
    class Meta:
        model = models.Contacto
        fields = ['nombre', 'numero_contacto', 'email', 'mensaje']
        labels = {
            'nombre': 'Nombre',
            'numero_contacto': 'Número de contacto',
            'email': 'Correo electrónico',
            'mensaje': 'Mensaje',
        }
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 4}),
        }
