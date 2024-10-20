import datetime
from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.db.models import F 
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from dullnane_detector.utils import phone_regex, valida_cedula, valida_numero_flotante_positivo, valida_numero_entero_positivo
import os

class Nivel(models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=150, unique=True)
    descripcion = models.TextField(verbose_name='Descripción', null=True, blank=True)
    orden = models.PositiveIntegerField(default=0, verbose_name='Orden') 
    imagen = models.ImageField(upload_to='niveles/', null=True, blank=True, verbose_name='Imagen')  

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Nivel'
        verbose_name_plural = 'Niveles'
        ordering = ['orden'] 


class Leccion(models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=150)
    descripcion = models.TextField(verbose_name='Descripción', null=True, blank=True)
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    orden = models.IntegerField(verbose_name='Orden', default=0) 

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Lección'
        verbose_name_plural = 'Lecciones'
        ordering = ['orden']  


class Progreso(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE)
    completado = models.BooleanField(verbose_name='Completado', default=False)
    desbloqueado = models.BooleanField(default=False)
    intentos = models.IntegerField(verbose_name='Número de Intentos', default=0)  

    def __str__(self):
        return f'{self.usuario.username} - {self.nivel.name} - {"Desbloqueado" if self.desbloqueado else "Bloqueado"}'

    class Meta:
        verbose_name = 'Progreso'
        verbose_name_plural = 'Progresos'
        ordering = ['usuario', 'nivel', 'leccion']


class Senal(models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=150)
    descripcion = models.TextField(verbose_name='Descripción', null=True, blank=True)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE)
    imagen = models.ImageField(verbose_name='Imagen de Ejemplo', upload_to='senales/')
    video = models.FileField(verbose_name='Video de Ejemplo', upload_to='videos/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Señal'
        verbose_name_plural = 'Señales'
        ordering = ['name']


class Feedback(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE)
    progreso = models.ForeignKey(Progreso, on_delete=models.CASCADE, null=True, blank=True) 
    intento_correcto = models.BooleanField(verbose_name='Intento Correcto', default=False)
    fecha_intento = models.DateTimeField(verbose_name='Fecha de Intento', auto_now_add=True)
    intentos_incorrectos = models.IntegerField(verbose_name='Intentos Incorrectos', default=0) 
    mensaje = models.TextField(verbose_name='Mensaje de Feedback', null=True, blank=True)

    def __str__(self):
        return f'Feedback - {self.usuario.username} - Lección: {self.leccion.name}'

