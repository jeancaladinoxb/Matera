import re
from dataclasses import dataclass
from typing import Optional

from .errors import IdentificadorPanelInvalidoError, ValorPanelInvalidoError


_MAC_PATTERN = re.compile(r"[0-9A-F]{12}")


@dataclass(frozen=True)
class MateraPanel:
    matera_id: int
    mac: str
    planta_id: Optional[int] = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.matera_id, bool)
            or not isinstance(self.matera_id, int)
            or self.matera_id <= 0
        ):
            raise IdentificadorPanelInvalidoError()
        if not isinstance(self.mac, str) or _MAC_PATTERN.fullmatch(self.mac) is None:
            raise ValorPanelInvalidoError()
        if self.planta_id is not None and (
            isinstance(self.planta_id, bool)
            or not isinstance(self.planta_id, int)
            or self.planta_id <= 0
        ):
            raise IdentificadorPanelInvalidoError()

    @property
    def dispositivo_id(self) -> int:
        return self.matera_id
