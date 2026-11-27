"""
Derechos de los titulares de datos (Ley 21.719):
- acceso y portabilidad  -> export_user_data
- supresión              -> delete_account (anonimiza)
"""
import uuid

from django.db import transaction
from django.utils import timezone

from apps.core.services import audit, client_ip

from .models import Consent


def record_consent(user, *, version, request=None):
    return Consent.objects.create(user=user, version=version, ip_address=client_ip(request))


def export_user_data(user) -> dict:
    """Todos los datos personales del usuario en un formato legible por máquina (JSON)."""
    data = {
        "generado": timezone.now().isoformat(),
        "cuenta": {"email": user.email, "rol": user.role, "creada": user.date_joined.isoformat()},
        "consentimientos": [
            {"documento": c.document, "version": c.version, "aceptado": c.accepted_at.isoformat()}
            for c in user.consents.all()
        ],
    }
    if hasattr(user, "electrician_profile"):
        p = user.electrician_profile
        data["perfil_electricista"] = {
            "nombre": p.full_name, "telefono": p.phone, "presentacion": p.bio,
            "comunas": [c.name for c in p.comunas.all()],
            "verificacion": p.verification_status, "clase_licencia": p.license_class,
            "certificados": [{"subido": c.created_at.isoformat(), "estado": c.status}
                             for c in p.certificates.all()],
            "trabajos": [{"codigo": j.code, "descripcion": j.description, "estado": j.status}
                         for j in p.jobs.all()],
        }
    if hasattr(user, "client_profile"):
        p = user.client_profile
        data["perfil_cliente"] = {
            "nombre": p.full_name, "telefono": p.phone,
            "comuna": p.comuna.name if p.comuna else None,
            "instalaciones": [{"nombre": i.name, "direccion": i.address} for i in p.installations.all()],
        }
    return data


@transaction.atomic
def delete_account(user, request=None):
    """
    Supresión: se borran o anonimizan los datos personales. Los trabajos se
    conservan sin datos que identifiquen a la persona (el electricista necesita su
    historial y la ley permite conservar lo necesario por obligaciones legales).
    """
    audit(user, "privacy.account_deleted", target=user, request=request)

    if hasattr(user, "electrician_profile"):
        p = user.electrician_profile
        for cert in p.certificates.all():
            cert.file.delete(save=False)  # el certificado trae RUT: se elimina el archivo
            cert.delete()
        p.full_name = "Electricista eliminado"
        p.phone = f"5690{uuid.uuid4().int % 10**7:07d}"  # valor único sin significado
        p.bio = ""
        p.save()
        p.comunas.clear()

    if hasattr(user, "client_profile"):
        p = user.client_profile
        for inst in p.installations.all():
            inst.address = "Dirección eliminada"
            inst.contact_name = ""
            inst.contact_phone = ""
            inst.save()
            inst.qr_tokens.update(is_active=False)
        p.full_name = "Cliente eliminado"
        p.phone = ""
        p.save()

    user.email = f"eliminado-{uuid.uuid4().hex}@invalid.local"
    user.set_unusable_password()
    user.is_active = False
    user.save()
