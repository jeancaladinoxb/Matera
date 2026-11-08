import os
from datetime import datetime, timedelta, timezone

import jwt

from backend.materas.application.ports.output import DeviceTokenProviderPort
from backend.materas.domain import Mac


_ALGORITHM = "HS256"
_MIN_SECRET_LENGTH = 32
_DEFAULT_EXPIRATION_DAYS = 365
DEVICE_ROLE = "device"


class JwtDeviceTokenAdapter(DeviceTokenProviderPort):
    """Device JWT: sub = normalized MAC, role = "device".

    Signed with its own secret, so a user token never validates as a device
    token and the other way around.
    """

    def __init__(
        self, secret: str, expiration_days: int = _DEFAULT_EXPIRATION_DAYS
    ) -> None:
        if not isinstance(secret, str) or len(secret) < _MIN_SECRET_LENGTH:
            raise ValueError(
                "DEVICE_JWT_SECRET debe tener al menos {} caracteres.".format(
                    _MIN_SECRET_LENGTH
                )
            )
        if (
            isinstance(expiration_days, bool)
            or not isinstance(expiration_days, int)
            or expiration_days <= 0
        ):
            raise ValueError(
                "DEVICE_JWT_EXPIRATION_DAYS debe ser un entero positivo."
            )

        self._secret = secret
        self._expiration = timedelta(days=expiration_days)

    def generar_token(self, mac: Mac) -> str:
        issued_at = datetime.now(timezone.utc)
        payload = {
            "sub": mac.value,
            "role": DEVICE_ROLE,
            "iat": issued_at,
            "exp": issued_at + self._expiration,
        }
        return jwt.encode(payload, self._secret, algorithm=_ALGORITHM)


def jwt_device_token_adapter_from_environment() -> JwtDeviceTokenAdapter:
    """Read and validate the device JWT configuration once, at startup."""
    secret = os.environ.get("DEVICE_JWT_SECRET", "").strip()
    if not secret:
        raise ValueError("Falta la variable de configuración DEVICE_JWT_SECRET.")
    if secret == os.environ.get("JWT_SECRET", "").strip():
        raise ValueError("DEVICE_JWT_SECRET debe ser distinto de JWT_SECRET.")

    raw_days = os.environ.get("DEVICE_JWT_EXPIRATION_DAYS", "").strip()
    if not raw_days:
        return JwtDeviceTokenAdapter(secret)
    try:
        expiration_days = int(raw_days)
    except ValueError:
        raise ValueError(
            "DEVICE_JWT_EXPIRATION_DAYS debe ser un entero positivo."
        ) from None
    return JwtDeviceTokenAdapter(secret, expiration_days)
