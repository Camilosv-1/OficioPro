# Imagen del backend Django. "slim" = imagen base pequeña (menos paquetes = menos vulnerabilidades).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Librerías del sistema que necesita WeasyPrint para generar PDF.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Primero solo requirements: Docker reutiliza esta capa si no cambian las dependencias.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Usuario sin privilegios: si alguien compromete la app, no es root dentro del contenedor.
RUN useradd --create-home --uid 1000 appuser \
 && mkdir -p /app/private_media /app/staticfiles \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health/')"

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
