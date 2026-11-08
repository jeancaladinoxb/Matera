import re
from dataclasses import dataclass

from .errors import InvalidMacError


_MAC_PATTERN = re.compile(r"[0-9A-F]{12}")
_SEPARATORS = re.compile(r"[:\-.]")


@dataclass(frozen=True)
class Mac:
    """MAC address in its normalized form: 12 uppercase hex digits, no separators."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidMacError()

        normalized = _SEPARATORS.sub("", self.value.strip()).upper()

        if _MAC_PATTERN.fullmatch(normalized) is None:
            raise InvalidMacError()

        object.__setattr__(self, "value", normalized)
