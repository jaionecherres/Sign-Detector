from django import forms
from app.security.models import Module

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = '__all__'
        widgets = {
            'url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL del módulo'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del módulo'
            }),
            'menu': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del módulo'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Icono del módulo'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'permissions': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'url': 'URL',
            'name': 'Nombre',
            'menu': 'Menú',
            'description': 'Descripción',
            'icon': 'Icono',
            'is_active': 'Es activo',
            'permissions': 'Permisos',
        }
