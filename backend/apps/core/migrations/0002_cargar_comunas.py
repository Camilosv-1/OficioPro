"""Migración de DATOS: carga las comunas de Santiago una sola vez."""
from django.db import migrations

from apps.core.constants import COMUNAS_SANTIAGO


def cargar(apps, schema_editor):
    Comuna = apps.get_model("core", "Comuna")
    for nombre in COMUNAS_SANTIAGO:
        Comuna.objects.get_or_create(name=nombre)


def borrar(apps, schema_editor):
    apps.get_model("core", "Comuna").objects.filter(name__in=COMUNAS_SANTIAGO).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(cargar, borrar)]
