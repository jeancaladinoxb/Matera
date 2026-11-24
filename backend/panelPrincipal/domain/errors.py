class PanelPrincipalDomainError(Exception):
    """Base class for panel domain errors."""


class ValorPanelInvalidoError(PanelPrincipalDomainError):
    def __init__(self) -> None:
        super().__init__("Un valor del panel principal no es válido.")


class IdentificadorPanelInvalidoError(PanelPrincipalDomainError):
    def __init__(self) -> None:
        super().__init__("Un identificador del panel principal no es válido.")
