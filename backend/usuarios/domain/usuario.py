from dataclasses import dataclass, field

from .email import Email
from .errors import MissingRequiredFieldError
from .password import Password


@dataclass(frozen=True)
class Usuario:
    nombre: str
    apellido: str
    nickname: str
    correo: Email
    contrasena: Password = field(repr=False)

    def __post_init__(self) -> None:
        required_text_fields = (self.nombre, self.apellido, self.nickname)
        if any(
            not isinstance(value, str) or not value.strip()
            for value in required_text_fields
        ):
            raise MissingRequiredFieldError()
