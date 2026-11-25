class DomainError(Exception):
    """Base class for errors that represent a plantas domain rule violation."""


class ValidationError(DomainError):
    """Base class for invalid domain values."""


class PlantaInvalidaError(ValidationError):
    def __init__(self, message: str = "La planta no es válida.") -> None:
        super().__init__(message)


class PlantaIdInvalidoError(ValidationError):
    def __init__(self) -> None:
        super().__init__("El id de la planta no es válido.")


class MateraIdInvalidoError(ValidationError):
    def __init__(self) -> None:
        super().__init__("El id de la matera no es válido.")


class PlantaNoEncontradaError(DomainError):
    def __init__(self) -> None:
        super().__init__("La planta no existe.")


class MateraNoEncontradaError(DomainError):
    """The matera does not exist, is not linked, or belongs to another user.

    One error for all three cases keeps the API from revealing which materas exist.
    """

    def __init__(self) -> None:
        super().__init__("La matera no existe o no es del usuario.")
