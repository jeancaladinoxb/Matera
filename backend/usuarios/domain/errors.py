class DomainError(Exception):
    """Base class for errors that represent a domain rule violation."""


class ValidationError(DomainError):
    """Base class for invalid domain values."""


class InvalidEmailError(ValidationError):
    def __init__(self) -> None:
        super().__init__("El correo electrónico no tiene un formato válido.")


class InvalidPasswordError(ValidationError):
    def __init__(self) -> None:
        super().__init__(
            "La contraseña debe tener al menos 8 caracteres, ser alfanumérica "
            "y contener al menos una mayúscula."
        )


class MissingRequiredFieldError(ValidationError):
    def __init__(self) -> None:
        super().__init__("Faltan campos obligatorios.")


class EmailAlreadyRegisteredError(DomainError):
    def __init__(self) -> None:
        super().__init__("El correo ya está registrado.")


class InvalidCredentialsError(DomainError):
    def __init__(self) -> None:
        super().__init__("Credenciales inválidas.")


class InvalidTokenError(DomainError):
    def __init__(self) -> None:
        super().__init__("Token inválido.")
