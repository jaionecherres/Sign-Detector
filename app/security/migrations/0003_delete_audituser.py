# Generated by Django 4.2 on 2024-10-21 00:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0002_dashboard'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AuditUser',
        ),
    ]
