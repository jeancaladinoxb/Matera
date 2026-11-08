class DomainError(Exception):
    """Base class for errors that represent a domain rule violation."""


class ValidationError(DomainError):
    """Base class for invalid domain values."""


class InvalidMacError(ValidationError):
    def __init__(self) -> None:
        super().__init__("La MAC no tiene un formato válido.")


class MateraOCodigoInvalidoError(DomainError):
    """Same error for an invalid claim code and for an unknown matera.

    Using one error for both keeps the API from revealing which MACs exist.
    """

    def __init__(self) -> None:
        super().__init__("Matera o código inválido.")


class MateraYaVinculadaError(DomainError):
    def __init__(self) -> None:
        super().__init__("La matera ya está vinculada.")


class MateraNoVinculadaError(DomainError):
    def __init__(self) -> None:
        super().__init__("La matera aún no está vinculada.")
