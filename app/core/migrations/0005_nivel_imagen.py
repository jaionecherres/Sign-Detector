# Generated by Django 4.2 on 2024-10-17 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_nivel_options_nivel_orden'),
    ]

    operations = [
        migrations.AddField(
            model_name='nivel',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='niveles/', verbose_name='Imagen'),
        ),
    ]