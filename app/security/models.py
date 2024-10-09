import json
from crum import get_current_request
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.forms import model_to_dict
#from app.core.models import Progreso,Feedback,Nivel

# ficha,prestamos,nomina
class Menu(models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=150, unique=True)
    icon = models.CharField(verbose_name='Icono', max_length=100)
  
    def __str__(self):
        return self.name

    def get_model_to_dict(self):
        item = model_to_dict(self)
        return item

    def get_icon(self):
        if self.icon:
            return self.icon
        return 'bi bi-calendar-x-fill'

    class Meta:
        verbose_name = 'Menu'
        verbose_name_plural = 'Menus'
        ordering = ['-name']

# menu ficha: modulos: empleado, cargo
# permisos: add_empleado, view_empleado, change_empleado, delete_empleado
class Module(models.Model):
    url = models.CharField(verbose_name='Url', max_length=100, unique=True)
    name = models.CharField(verbose_name='Nombre', max_length=100)
    menu = models.ForeignKey(Menu, on_delete=models.PROTECT,verbose_name='Menu')
    description = models.CharField(
        verbose_name='Descripción',
        max_length=200,
        null=True,
        blank=True
    )
    icon = models.CharField(verbose_name='Icono', max_length=100, null=True,
                            blank=True)
    is_active = models.BooleanField(verbose_name='Es activo', default=True)
    permissions = models.ManyToManyField(
        verbose_name='Permisos',
        to=Permission,
        blank=True
    )

   
    def __str__(self):
        return '{} [{}]'.format(self.name, self.url)

    def get_model_to_dict(self):
        item = model_to_dict(self)
        return item

    def get_icon(self):
        if self.icon:
            return self.icon
        return 'bi bi-x-octagon'

    class Meta:
        verbose_name = 'Modulo'
        verbose_name_plural = 'Modulos'
        ordering = ('-name',)
# grupo: menu:     modulos : add,view...
# admi: ficha: sobretiempo,rubros: add_sobretiemp,view_sobretiemp,add_rubros,view_rubros
# auditoria: sobretiempo,rubros: add_sobretiemp,view_sobretiemp,add_rubros,view_rubros
class GroupModulePermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT,verbose_name='Grupo')
    module = models.ForeignKey(Module, on_delete=models.PROTECT,verbose_name='Modulo')
    permissions = models.ManyToManyField(Permission)
    

    def __str__(self):
        return f"{self.module.name} -{self.group.name}"

    @staticmethod
    # obtiene los modulos con su respectivo menu del grupo requerido
    def get_group_module_permission_active_list(group_id):
        return GroupModulePermission.objects.select_related(
            'module',
            'module__menu'
        ).filter(
            group_id=group_id,
            module__is_active=True
        )

    class Meta:
        verbose_name = 'Grupo modulo permiso'
        verbose_name_plural = 'Grupos modulos Permisos'
        ordering = ('-id',)
        
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un email.')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, username, first_name, last_name, password, **extra_fields)


class User(AbstractUser):
    image = models.ImageField(
        verbose_name='Archive image',
        upload_to='users/',
        max_length=1024,
        blank=True,
        null=True
    )
    email = models.EmailField('Email',unique=True)
    direction=models.CharField('Direccion',max_length=200,blank=True,null=True)
    phone=models.CharField('Telefono',max_length=50,blank=True,null=True)
  
    USERNAME_FIELD = "email" # cambia el login
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = CustomUserManager()
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        # crea un nuevo permiso al modelo
        permissions = (
            (
                "change_userprofile",
                f"Cambiar perfil {verbose_name}"
            ),
            (
                "change_userpassword",
                f"Cambiar password {verbose_name}"
            ),
          
        )
    
    # def save(self, *args, **kwargs):
    #     # Comprueba si la contraseña ha cambiado
    #     if self.pk is None or not User.objects.filter(pk=self.pk, password=self.password).exists():
    #         self.set_password(self.password)
    #     super().save(*args, **kwargs)
        
    def __str__(self):
        return '{}'.format(self.username)

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_groups(self):
        return self.groups.all()

    def get_short_name(self):
        return self.username

    def get_group_session(self):
        request = get_current_request()
        print("request==>",request)
        return Group.objects.get(pk=request.session['group_id'])

    def set_group_session(self):
        request = get_current_request()

        if 'group' not in request.session:

            groups = request.user.groups.all().order_by('id')

            if groups.exists():
                request.session['group'] = groups.first()
                request.session['group_id'] = request.session['group'].id

    
    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return '/static/img/usuario_anonimo.png'

class AuditUser(models.Model):
    TIPOS_ACCIONES = (
        ('A', 'A'),   # Adicion
        ('M', 'M'),   # Modificacion
        ('E', 'E')    # Eliminacion
    )
    usuario = models.ForeignKey(User, verbose_name='Usuario',on_delete=models.PROTECT)
    tabla = models.CharField(max_length=100, verbose_name='Tabla')
    registroid = models.IntegerField(verbose_name='Registro Id')
    accion = models.CharField(choices=TIPOS_ACCIONES, max_length=10, verbose_name='Accion')
    fecha = models.DateField(verbose_name='Fecha')
    hora = models.TimeField(verbose_name='Hora')
    estacion = models.CharField(max_length=100, verbose_name='Estacion')

    def __str__(self):
        return "{} - {} [{}]".format(self.usuario.username, self.tabla, self.accion)

    class Meta:
        verbose_name = 'Auditoria Usuario '
        verbose_name_plural = 'Auditorias Usuarios'
        ordering = ('-fecha', 'hora')

# security/models.py

# class Dashboard(models.Model):
#     usuario = models.OneToOneField(User, on_delete=models.CASCADE)
#     nivel_actual = models.ForeignKey(Nivel, on_delete=models.SET_NULL, null=True)
#     lecciones_completadas = models.IntegerField(verbose_name='Lecciones Completadas', default=0)
#     total_intentos = models.IntegerField(verbose_name='Total de Intentos', default=0)
#     intentos_exitosos = models.IntegerField(verbose_name='Intentos Exitosos', default=0)
#     porcentaje_exito = models.DecimalField(verbose_name='Porcentaje de Éxito', max_digits=5, decimal_places=2, default=0.0)

#     def actualizar_dashboard(self):
#         progreso_niveles = Progreso.objects.filter(usuario=self.usuario, completado=True)
#         self.lecciones_completadas = progreso_niveles.count()
        
#         intentos_totales = Feedback.objects.filter(usuario=self.usuario).count()
#         intentos_correctos = Feedback.objects.filter(usuario=self.usuario, intento_correcto=True).count()
        
#         self.total_intentos = intentos_totales
#         self.intentos_exitosos = intentos_correctos
#         self.porcentaje_exito = (intentos_correctos / intentos_totales) * 100 if intentos_totales > 0 else 0.0
#         self.save()

#     def __str__(self):
#         return f'Dashboard - {self.usuario.username}'
