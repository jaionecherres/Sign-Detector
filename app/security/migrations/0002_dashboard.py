# Generated by Django 4.2 on 2024-10-13 21:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_initial'),
        ('security', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lecciones_completadas', models.IntegerField(default=0, verbose_name='Lecciones Completadas')),
                ('total_intentos', models.IntegerField(default=0, verbose_name='Total de Intentos')),
                ('intentos_exitosos', models.IntegerField(default=0, verbose_name='Intentos Exitosos')),
                ('porcentaje_exito', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Porcentaje de Éxito')),
                ('nivel_actual', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.nivel')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]