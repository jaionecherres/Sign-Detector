from django.forms import ModelForm
from django import forms
from app.core.models import Level  # Asegúrate de que el modelo Level esté correctamente importado

class LevelForm(ModelForm):
    class Meta:
        model = Level
        fields = ["name", "description", "active"]  # Ajusta los campos según tu modelo
        error_messages = {
            "name": {
                "unique": "Ya existe un nivel con este nombre.",
            },
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Ingrese nombre del nivel",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Ingrese descripción del nivel",
                    "class": "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
                }
            ),
            "active": forms.CheckboxInput(
                attrs={
                    "class": "mt-1 block px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                }
            ),
        }
        labels = {
            "name": "Nombre",
            "description": "Descripción",
            "active": "Activo",
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        return name.upper()  # Asegúrate de que el nombre esté en mayúsculas
