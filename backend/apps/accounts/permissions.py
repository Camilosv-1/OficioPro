"""
Permisos por ROL (RBAC). Se combinan en las vistas, por ejemplo:
    permission_classes = [IsAuthenticated, IsElectrician]

Los permisos por OBJETO (¿este trabajo es tuyo?) se resuelven en los
selectores de cada módulo, filtrando siempre por el usuario conectado.
"""
from rest_framework.permissions import BasePermission


class IsElectrician(BasePermission):
    message = "Solo los electricistas pueden hacer esto."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_electrician
                    and hasattr(user, "electrician_profile"))


class IsClient(BasePermission):
    message = "Solo los clientes pueden hacer esto."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_client and hasattr(user, "client_profile"))


class IsPlatformAdmin(BasePermission):
    message = "Solo el administrador puede hacer esto."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_platform_admin)
