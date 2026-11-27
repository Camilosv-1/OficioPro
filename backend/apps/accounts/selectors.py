"""Consultas (lecturas) de cuentas."""
from django.db.models import Case, IntegerField, Value, When

from .models import ElectricianProfile


def search_electricians(comuna: str | None = None):
    """Electricistas activos de una comuna; primero los que tienen insignia SEC."""
    qs = (ElectricianProfile.objects
          .filter(user__is_active=True)
          .prefetch_related("comunas")
          .annotate(badge_order=Case(
              When(verification_status=ElectricianProfile.Verification.VERIFIED, then=Value(0)),
              default=Value(1), output_field=IntegerField()))
          .order_by("badge_order", "full_name"))
    if comuna:
        qs = qs.filter(comunas__name=comuna)
    return qs
