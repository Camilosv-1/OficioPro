"""
Serializers = capa de presentación: validan la ENTRADA y dan forma a la SALIDA.
Nunca se devuelve un modelo completo: se elige campo por campo qué se muestra
(minimización de datos, Ley 21.719).
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.core.constants import COMUNAS_SANTIAGO
from apps.privacy.constants import PRIVACY_POLICY_VERSION

from .models import ElectricianProfile, User, phone_validator


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=10)
    role = serializers.ChoiceField(choices=[User.Role.ELECTRICIAN, User.Role.CLIENT])
    full_name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=11, validators=[phone_validator], required=False, allow_blank=True)
    comunas = serializers.ListField(child=serializers.ChoiceField(choices=COMUNAS_SANTIAGO),
                                    required=False, max_length=34)
    accept_privacy_policy = serializers.BooleanField()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe una cuenta con este email.")
        return value.lower()

    def validate_accept_privacy_policy(self, value):
        if value is not True:
            raise serializers.ValidationError("Debes aceptar la política de privacidad.")
        return value

    def validate(self, attrs):
        validate_password(attrs["password"])
        if attrs["role"] == User.Role.ELECTRICIAN and not attrs.get("phone"):
            raise serializers.ValidationError({"phone": "El teléfono es obligatorio para electricistas."})
        if attrs["role"] == User.Role.ELECTRICIAN and ElectricianProfile.objects.filter(
                phone=attrs["phone"]).exists():
            raise serializers.ValidationError({"phone": "Este teléfono ya está registrado."})
        attrs["privacy_version"] = PRIVACY_POLICY_VERSION
        return attrs


class ElectricianOwnProfileSerializer(serializers.ModelSerializer):
    """Lo que el electricista ve y edita de sí mismo."""

    comunas = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)
    has_badge = serializers.BooleanField(read_only=True)

    class Meta:
        model = ElectricianProfile
        fields = ["full_name", "phone", "bio", "comunas", "verification_status",
                  "license_class", "has_badge"]
        read_only_fields = ["verification_status", "license_class"]


class ElectricianPublicSerializer(serializers.ModelSerializer):
    """Lo que ve un cliente: sin teléfono en texto, sin certificado, sin estado interno."""

    id = serializers.IntegerField(read_only=True)
    comunas = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)
    badge = serializers.SerializerMethodField()
    whatsapp_url = serializers.SerializerMethodField()

    class Meta:
        model = ElectricianProfile
        fields = ["id", "full_name", "bio", "comunas", "badge", "whatsapp_url"]

    def get_badge(self, obj):
        return f"SEC verificado – Clase {obj.license_class}" if obj.has_badge else None

    def get_whatsapp_url(self, obj):
        return f"https://wa.me/{obj.phone}"


class MeSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "role", "profile"]

    def get_profile(self, user):
        if user.is_electrician and hasattr(user, "electrician_profile"):
            return ElectricianOwnProfileSerializer(user.electrician_profile).data
        if user.is_client and hasattr(user, "client_profile"):
            p = user.client_profile
            return {"full_name": p.full_name, "phone": p.phone,
                    "comuna": p.comuna.name if p.comuna else None}
        return None


class ElectricianUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=120, required=False)
    phone = serializers.CharField(max_length=11, validators=[phone_validator], required=False)
    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    comunas = serializers.ListField(child=serializers.ChoiceField(choices=COMUNAS_SANTIAGO), required=False)
