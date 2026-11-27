"""Rutas principales: cada módulo publica sus propias URLs bajo /api/."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Ruta del admin de Django poco predecible (reduce ataques automatizados).
    path("admin-oficiopro/", admin.site.urls),
    path("api/", include("apps.core.urls")),
    path("api/auth/", include("apps.accounts.urls")),
    # path("api/privacy/", include("apps.privacy.urls")),
    # path("api/verification/", include("apps.verification.urls")),
    # path("api/installations/", include("apps.clients.urls")),
    # path("api/jobs/", include("apps.jobs.urls")),
    # path("api/materials/", include("apps.materials.urls")),
    # path("api/quotes/", include("apps.quotes.urls")),
    # path("api/qr/", include("apps.qr.urls")),
    # path("api/whatsapp/", include("apps.whatsapp.urls")),
]