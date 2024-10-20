from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from app.security.models import User
from app.core.models import Progreso, Nivel, Leccion  # Importa tus modelos

@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        #Si el usuario es un superusuario, asignarle el grupo "Administradores"
        if instance.is_superuser:
            print(f"Asignando grupo de administradores a {instance.username}")
            admin_group, created = Group.objects.get_or_create(name='Administradores')
            instance.groups.add(admin_group)
        else:
            #Si el usuario NO es superusuario, desbloquear el Nivel 1
            print(f"Desbloqueando Nivel 1 para el usuario {instance.username}")
            alfabeto = Nivel.objects.get(orden=1)  #Obtener el Nivel 1
            primera_leccion = Leccion.objects.filter(nivel=alfabeto).first()  #Obtener la primera lección del Nivel 1
            Progreso.objects.create(usuario=instance, nivel=alfabeto, leccion=primera_leccion, desbloqueado=True)

            print(f"Nivel 1 y la primera lección desbloqueados para {instance.username}")
