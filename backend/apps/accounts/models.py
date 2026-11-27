"""
Usuarios y perfiles.

- User: credenciales y ROL (electricista, cliente, admin). Inicia sesión con email.
- ElectricianProfile / ClientProfile: datos de cada tipo de usuario (composición:
  un usuario "tiene un" perfil, relación uno a uno).
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models

from apps.core.models import Comuna, TimeStampedModel

# Teléfono chileno en formato internacional sin "+": 56 + 9 + 8 dígitos.
phone_validator = RegexValidator(r"^569\d{8}$", "Usa el formato 569XXXXXXXX (sin + ni espacios).")


class UserManager(BaseUserManager):
    """Administrador de usuarios que usa email en vez de nombre de usuario."""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("El email es obligatorio")
        user = self.model(email=self.normalize_email(email).lower(), **extra)
        user.set_password(password)  # guarda el HASH, nunca la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.update(is_staff=True, is_superuser=True, role=User.Role.ADMIN)
        return self.create_user(email, password, **extra)


class User(AbstractUser):
    class Role(models.TextChoices):
        ELECTRICIAN = "electrician", "Electricista"
        CLIENT = "client", "Cliente"
        ADMIN = "admin", "Administrador"

    username = None
    first_name = None
    last_name = None
    email = models.EmailField("email", unique=True)
    role = models.CharField("rol", max_length=20, choices=Role.choices, default=Role.CLIENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    @property
    def is_electrician(self):
        return self.role == self.Role.ELECTRICIAN

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_platform_admin(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return self.email


class ElectricianProfile(TimeStampedModel):
    class Verification(models.TextChoices):
        UNVERIFIED = "unverified", "Sin certificado"
        PENDING = "pending", "En revisión"
        VERIFIED = "verified", "Verificado"
        REJECTED = "rejected", "Rechazado"

    class LicenseClass(models.TextChoices):
        A = "A", "Clase A"
        B = "B", "Clase B"
        C = "C", "Clase C"
        D = "D", "Clase D"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="electrician_profile")
    full_name = models.CharField("nombre", max_length=120)
    phone = models.CharField("teléfono", max_length=11, validators=[phone_validator], unique=True)
    comunas = models.ManyToManyField(Comuna, related_name="electricians", blank=True)
    bio = models.TextField("presentación", blank=True, max_length=500)
    verification_status = models.CharField(max_length=20, choices=Verification.choices,
                                           default=Verification.UNVERIFIED)
    license_class = models.CharField(max_length=1, choices=LicenseClass.choices, blank=True)

    @property
    def has_badge(self) -> bool:
        """La insignia SEC solo se muestra si el admin aprobó el certificado."""
        return self.verification_status == self.Verification.VERIFIED and bool(self.license_class)

    def __str__(self):
        return self.full_name


class ClientProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    full_name = models.CharField("nombre", max_length=120)
    phone = models.CharField("teléfono", max_length=11, validators=[phone_validator], blank=True)
    comuna = models.ForeignKey(Comuna, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.full_name
