"""
Modelos base compartidos por todos los módulos.

TimeStampedModel es una clase ABSTRACTA: no crea tabla propia, solo entrega
campos a las clases que heredan de ella (herencia en POO).
"""
from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("modificado", auto_now=True)

    class Meta:
        abstract = True


class Comuna(models.Model):
    """Comunas donde opera la app. Tabla propia = datos normalizados (sin texto libre)."""

    name = models.CharField("nombre", max_length=60, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    """Registro de auditoría: quién hizo qué y cuándo. No se edita ni se borra."""

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                              on_delete=models.SET_NULL, related_name="audit_events")
    action = models.CharField("acción", max_length=100)
    target_type = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action}"

