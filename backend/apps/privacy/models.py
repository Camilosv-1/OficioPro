from django.conf import settings
from django.db import models


class Consent(models.Model):
    """Evidencia del consentimiento: quién aceptó, qué versión y cuándo (Ley 21.719)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consents")
    document = models.CharField(max_length=50, default="privacy_policy")
    version = models.CharField(max_length=20)
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-accepted_at"]
