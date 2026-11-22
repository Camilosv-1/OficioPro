"""
Validación y limpieza de archivos subidos por usuarios.

Regla de seguridad: NUNCA confiar en el nombre ni en la extensión que manda el
usuario. Se revisa el contenido real del archivo y se guarda con un nombre aleatorio.
"""
import io
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, UnidentifiedImageError

ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_IMAGE_SIDE = 1600  # px


def random_filename(extension: str) -> str:
    return f"{uuid.uuid4().hex}.{extension.lstrip('.')}"


def sanitize_image(uploaded_file) -> ContentFile:
    """
    1) Verifica que sea una imagen real (no un .exe renombrado a .jpg).
    2) La reduce a 1600 px como máximo.
    3) La vuelve a guardar como JPEG: así se eliminan los metadatos EXIF
       (que pueden incluir la ubicación GPS de la casa del cliente).
    """
    if uploaded_file.size > settings.MAX_IMAGE_BYTES:
        raise ValidationError("La imagen supera el tamaño máximo permitido (5 MB).")
    try:
        probe = Image.open(uploaded_file)
        probe.verify()  # detecta archivos corruptos o falsos
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        if image.format not in ALLOWED_IMAGE_FORMATS:
            raise ValidationError("Formato no permitido. Usa JPG, PNG o WEBP.")
        image = image.convert("RGB")  # descarta canales y metadatos
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise ValidationError("El archivo no es una imagen válida.")

    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=80, optimize=True)  # sin exif=
    return ContentFile(buffer.getvalue(), name=random_filename("jpg"))


def validate_document(uploaded_file) -> str:
    """Acepta PDF o imagen para el certificado SEC. Devuelve la extensión segura."""
    if uploaded_file.size > settings.MAX_DOCUMENT_BYTES:
        raise ValidationError("El documento supera el tamaño máximo permitido (5 MB).")
    header = uploaded_file.read(5)
    uploaded_file.seek(0)
    if header == b"%PDF-":  # "número mágico" de los PDF
        return "pdf"
    try:
        Image.open(uploaded_file).verify()
        uploaded_file.seek(0)
        return "img"
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise ValidationError("El certificado debe ser un PDF o una imagen.")
