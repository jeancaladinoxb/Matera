import re
from dataclasses import dataclass

from .errors import InvalidEmailError


_EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+"
)
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidEmailError()

        normalized = self.value.strip().lower()

        if len(normalized) > 254 or _EMAIL_PATTERN.fullmatch(normalized) is None:
            raise InvalidEmailError()

        object.__setattr__(self, "value", normalized)
