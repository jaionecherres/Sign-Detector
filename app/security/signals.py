from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from app.security.models import User
from app.core.models import Progreso, Nivel, Leccion  # Importa tus modelos

@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        # Verificar si el usuario es superusuario, si es así, asignar el grupo Administradores
        if instance.is_superuser:
            admin_group, created = Group.objects.get_or_create(name='Administradores')
            instance.groups.add(admin_group)
        else:
            # Verificar si el usuario pertenece al grupo 'User'
            user_group = Group.objects.get(name='User')
            if user_group in instance.groups.all():
                # Si el usuario pertenece al grupo 'User', asignarle el nivel 1 desbloqueado
                try:
                    alfabeto = Nivel.objects.get(orden=1)
                    primera_leccion = Leccion.objects.filter(nivel=alfabeto).first()
                    
                    # Crear el progreso del usuario para el nivel 1 y desbloquearlo
                    Progreso.objects.create(
                        usuario=instance, 
                        nivel=alfabeto, 
                        leccion=primera_leccion, 
                        desbloqueado=True
                    )
                    print(f"Nivel 1 y la primera lección desbloqueados para el usuario {instance.username}")
                except Nivel.DoesNotExist:
                    print("El Nivel 1 no existe")
            else:
                # Si el usuario no pertenece al grupo 'User', asignarle el grupo 'User'
                instance.groups.add(user_group)
                print(f"Grupo 'User' asignado al usuario {instance.username}")
    else:
        # Si el usuario ya existe, solo se verifica si tiene asignado el grupo 'User'
        user_group = Group.objects.get(name='User')
        if user_group in instance.groups.all():
            # Si ya tiene el grupo 'User', asegurarse de que tenga el Nivel 1 desbloqueado
            if not Progreso.objects.filter(usuario=instance, nivel__orden=1).exists():
                try:
                    alfabeto = Nivel.objects.get(orden=1)
                    primera_leccion = Leccion.objects.filter(nivel=alfabeto).first()
                    Progreso.objects.create(
                        usuario=instance, 
                        nivel=alfabeto, 
                        leccion=primera_leccion, 
                        desbloqueado=True
                    )
                    print(f"Nivel 1 y la primera lección desbloqueados para el usuario {instance.username}")
                except Nivel.DoesNotExist:
                    print("El Nivel 1 no existe")
