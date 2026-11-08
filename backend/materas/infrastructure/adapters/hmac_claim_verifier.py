import hashlib
import hmac
import os

from backend.materas.application.ports.output import ClaimCodeVerifierPort
from backend.materas.domain import Mac


_MIN_KEY_LENGTH = 32
_CODE_LENGTH = 12


class HmacClaimVerifier(ClaimCodeVerifierPort):
    """code = HMAC_SHA256(master key, normalized MAC) as hex, first 12 chars.

    The code is never stored: it is recomputed on every check.
    """

    def __init__(self, master_key: str) -> None:
        if not isinstance(master_key, str) or len(master_key) < _MIN_KEY_LENGTH:
            raise ValueError(
                "CLAIM_MASTER_KEY debe tener al menos {} caracteres.".format(
                    _MIN_KEY_LENGTH
                )
            )
        self._master_key = master_key.encode("utf-8")

    def generar(self, mac: Mac) -> str:
        digest = hmac.new(
            self._master_key, mac.value.encode("ascii"), hashlib.sha256
        ).hexdigest()
        return digest[:_CODE_LENGTH]

    def verificar(self, mac: Mac, codigo: str) -> bool:
        if not isinstance(codigo, str):
            return False
        # Bytes, so a non-ASCII input cannot make compare_digest raise.
        return hmac.compare_digest(
            self.generar(mac).encode("ascii"), codigo.encode("utf-8")
        )


def hmac_claim_verifier_from_environment() -> HmacClaimVerifier:
    """Read CLAIM_MASTER_KEY once, at startup."""
    master_key = os.environ.get("CLAIM_MASTER_KEY", "").strip()
    if not master_key:
        raise ValueError("Falta la variable de configuración CLAIM_MASTER_KEY.")
    return HmacClaimVerifier(master_key)
