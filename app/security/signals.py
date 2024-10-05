
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.db.models.signals import post_migrate

from app.security.models import User

@receiver(post_save, sender=User)

def assign_user_group(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser:
            print(instance)
            admin_group, created = Group.objects.get_or_create(name='Administradores')
            instance.groups.add(admin_group)