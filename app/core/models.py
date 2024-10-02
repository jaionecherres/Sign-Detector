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

class Level(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Nivel'
        verbose_name_plural = 'Niveles'
        ordering = ['id']