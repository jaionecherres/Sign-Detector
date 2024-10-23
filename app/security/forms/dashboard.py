from django import forms
from app.security.models import Dashboard

class DashboardForm(forms.ModelForm):
    class Meta:
        model = Dashboard
        fields = '__all__'
        widgets = {
            'usuario': forms.Select(attrs={
                'class': 'form-control',
            }),
            'nivel_actual': forms.Select(attrs={
                'class': 'form-control',
            }),
            'lecciones_completadas': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lecciones completadas'
            }),
            'total_intentos': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total de intentos'
            }),
            'intentos_exitosos': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Intentos exitosos'
            }),
            'porcentaje_exito': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Porcentaje de éxito (%)',
                'step': '0.01'
            }),
        }
        labels = {
            'usuario': 'Usuario',
            'nivel_actual': 'Nivel Actual',
            'lecciones_completadas': 'Lecciones Completadas',
            'total_intentos': 'Total de Intentos',
            'intentos_exitosos': 'Intentos Exitosos',
            'porcentaje_exito': 'Porcentaje de Éxito (%)',
        }
