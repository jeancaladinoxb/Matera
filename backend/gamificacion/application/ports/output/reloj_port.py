from abc import ABC, abstractmethod
from datetime import datetime


class RelojPort(ABC):
    @abstractmethod
    def ahora(self) -> datetime:
        """Return the current timezone-aware datetime."""
