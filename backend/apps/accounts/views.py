"""Vistas de cuentas: reciben la petición, validan con el serializer y llaman al servicio."""
from axes.handlers.proxy import AxesProxyHandler
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import selectors, services
from .permissions import IsElectrician
from .serializers import (ElectricianPublicSerializer, ElectricianUpdateSerializer,
                          MeSerializer, RegisterSerializer)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "register"

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = services.register_user(
            email=data["email"], password=data["password"], role=data["role"],
            full_name=data["full_name"], phone=data.get("phone", ""),
            comuna_names=data.get("comunas"), privacy_version=data["privacy_version"],
            request=request)
        return Response(MeSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """Devuelve access (15 min) y refresh (1 día). Con límite de intentos."""

    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        # django-axes registra cada intento fallido; si la cuenta está bloqueada,
        # se responde 429 aunque la contraseña ahora sea correcta.
        credentials = {"email": str(request.data.get("email", "")).lower()}
        if AxesProxyHandler.is_locked(request._request, credentials):
            return Response({"detail": "Demasiados intentos fallidos. Intenta de nuevo en 15 minutos."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)
        return super().post(request, *args, **kwargs)


class RefreshView(TokenRefreshView):
    throttle_scope = "login"


class LogoutView(APIView):
    """Invalida el refresh token (lista negra) para cerrar la sesión de verdad."""

    def post(self, request):
        try:
            RefreshToken(request.data.get("refresh", "")).blacklist()
        except TokenError:
            return Response({"detail": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response(MeSerializer(request.user).data)


class ElectricianProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsElectrician]

    def patch(self, request):
        serializer = ElectricianUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        services.update_electrician_profile(
            request.user.electrician_profile, full_name=data.get("full_name"),
            phone=data.get("phone"), bio=data.get("bio"), comuna_names=data.get("comunas"))
        return Response(MeSerializer(request.user).data)


class ElectricianSearchView(generics.ListAPIView):
    """Búsqueda de electricistas por comuna. Requiere sesión (evita scraping masivo)."""

    serializer_class = ElectricianPublicSerializer

    def get_queryset(self):
        return selectors.search_electricians(self.request.query_params.get("comuna"))
