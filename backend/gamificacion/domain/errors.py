class GamificacionDomainError(Exception):
    """Base class for gamification domain errors."""


class EstadisticasInvalidasError(GamificacionDomainError):
    def __init__(self) -> None:
        super().__init__("Las estadísticas del jardinero no son válidas.")


class LogroInvalidoError(GamificacionDomainError):
    def __init__(self) -> None:
        super().__init__("La definición del logro no es válida.")
