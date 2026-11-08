import os
from datetime import datetime, timedelta, timezone

import jwt

from backend.usuarios.application.ports.output import TokenProviderPort
from backend.usuarios.domain import InvalidTokenError


_ALGORITHM = "HS256"
_MIN_SECRET_LENGTH = 32


class JwtTokenAdapter(TokenProviderPort):
    def __init__(self, secret: str, expiration_hours: int = 5) -> None:
        if not isinstance(secret, str) or len(secret) < _MIN_SECRET_LENGTH:
            raise ValueError(
                "JWT_SECRET debe tener al menos {} caracteres.".format(
                    _MIN_SECRET_LENGTH
                )
            )
        if (
            isinstance(expiration_hours, bool)
            or not isinstance(expiration_hours, int)
            or expiration_hours <= 0
        ):
            raise ValueError("JWT_EXPIRATION_HOURS debe ser un entero positivo.")

        self._secret = secret
        self._expiration = timedelta(hours=expiration_hours)

    def generar_token(self, usuario_id: int) -> str:
        issued_at = datetime.now(timezone.utc)
        payload = {
            "sub": str(usuario_id),
            "iat": issued_at,
            "exp": issued_at + self._expiration,
        }
        return jwt.encode(payload, self._secret, algorithm=_ALGORITHM)

    def verificar_token(self, token: str) -> int:
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=[_ALGORITHM],
                options={"require": ["exp", "sub"]},
            )
        except jwt.InvalidTokenError:
            raise InvalidTokenError() from None

        subject = claims["sub"]
        # Device tokens carry a role and a MAC as subject: never valid here.
        if "role" in claims or not (
            isinstance(subject, str) and subject.isascii() and subject.isdigit()
        ):
            raise InvalidTokenError()
        return int(subject)


def jwt_token_adapter_from_environment() -> JwtTokenAdapter:
    """Read and validate the JWT configuration once, at startup."""
    secret = os.environ.get("JWT_SECRET", "").strip()
    raw_hours = os.environ.get("JWT_EXPIRATION_HOURS", "").strip()
    missing = []
    if not secret:
        missing.append("JWT_SECRET")
    if not raw_hours:
        missing.append("JWT_EXPIRATION_HOURS")
    if missing:
        raise ValueError(
            "Faltan variables de configuración JWT: {}.".format(", ".join(missing))
        )
    try:
        expiration_hours = int(raw_hours)
    except ValueError:
        raise ValueError("JWT_EXPIRATION_HOURS debe ser un entero positivo.") from None
    return JwtTokenAdapter(secret, expiration_hours)
