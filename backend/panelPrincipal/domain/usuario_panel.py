from dataclasses import dataclass

from .errors import IdentificadorPanelInvalidoError, ValorPanelInvalidoError


@dataclass(frozen=True)
class UsuarioPanel:
    usuario_id: int
    nombre: str
    nickname: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.usuario_id, bool)
            or not isinstance(self.usuario_id, int)
            or self.usuario_id <= 0
        ):
            raise IdentificadorPanelInvalidoError()
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (self.nombre, self.nickname)
        ):
            raise ValorPanelInvalidoError()
