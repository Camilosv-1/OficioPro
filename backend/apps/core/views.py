from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .constants import COMUNAS_SANTIAGO


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Endpoint de salud: lo usan Docker y el equipo para saber si la API está viva."""
    return Response({"status": "ok", "service": "oficiopro-api"})


@api_view(["GET"])
@permission_classes([AllowAny])
def comunas(request):
    return Response(COMUNAS_SANTIAGO)
