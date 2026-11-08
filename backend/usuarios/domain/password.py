from dataclasses import dataclass, field

from .errors import InvalidPasswordError

_MIN_LENGTH = 8


@dataclass(frozen=True)
class Password:
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if (
            not isinstance(self.value, str)
            or len(self.value) < _MIN_LENGTH
            or not self.value.isalnum()
            or not any(character.isupper() for character in self.value)
        ):
            raise InvalidPasswordError()
