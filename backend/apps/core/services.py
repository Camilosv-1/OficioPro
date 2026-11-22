"""Servicios transversales: auditoría."""
from .models import AuditLog


def client_ip(request):
    """IP del cliente. Detrás del proxy, la real viene en X-Forwarded-For."""
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def audit(actor, action, target=None, detail=None, request=None):
    """Guarda un evento de auditoría. Se llama desde los servicios, nunca desde las vistas."""
    return AuditLog.objects.create(
        actor=actor if (actor is not None and actor.is_authenticated) else None,
        action=action,
        target_type=target.__class__.__name__ if target is not None else "",
        target_id=str(getattr(target, "pk", "")) if target is not None else "",
        detail=detail or {},
        ip_address=client_ip(request),
    )
