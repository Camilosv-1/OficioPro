"""
Casos de uso de cuentas. Las vistas solo llaman a estas funciones:
así la lógica de negocio queda en un solo lugar y se puede probar sin HTTP.
"""
from django.db import transaction

from apps.core.models import Comuna
from apps.core.services import audit
from apps.privacy.services import record_consent

from .models import ClientProfile, ElectricianProfile, User


@transaction.atomic  # o se crea todo (usuario + perfil + consentimiento) o nada
def register_user(*, email, password, role, full_name, phone="", comuna_names=None,
                  privacy_version, request=None) -> User:
    if role not in (User.Role.ELECTRICIAN, User.Role.CLIENT):
        raise ValueError("Rol no permitido en el registro")  # nadie se registra como admin

    user = User.objects.create_user(email=email, password=password, role=role)
    comunas = list(Comuna.objects.filter(name__in=comuna_names or []))

    if role == User.Role.ELECTRICIAN:
        profile = ElectricianProfile.objects.create(user=user, full_name=full_name, phone=phone)
        profile.comunas.set(comunas)
    else:
        ClientProfile.objects.create(user=user, full_name=full_name, phone=phone,
                                     comuna=comunas[0] if comunas else None)

    record_consent(user, version=privacy_version, request=request)
    audit(user, "account.registered", target=user, detail={"role": role}, request=request)
    return user


def update_electrician_profile(profile: ElectricianProfile, *, full_name=None, phone=None,
                               bio=None, comuna_names=None) -> ElectricianProfile:
    if full_name is not None:
        profile.full_name = full_name
    if phone is not None:
        profile.phone = phone
    if bio is not None:
        profile.bio = bio
    profile.full_clean(exclude=["user"])
    profile.save()
    if comuna_names is not None:
        profile.comunas.set(Comuna.objects.filter(name__in=comuna_names))
    return profile
