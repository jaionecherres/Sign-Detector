# Generated by Django 4.2 on 2024-10-21 00:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_progreso_desbloqueado'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='fecha_intento',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='intentos_incorrectos',
        ),
    ]
