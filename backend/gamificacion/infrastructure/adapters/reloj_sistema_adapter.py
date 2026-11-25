from datetime import datetime, timezone

from backend.gamificacion.application.ports.output import RelojPort


class RelojSistemaAdapter(RelojPort):
    def ahora(self) -> datetime:
        return datetime.now(timezone.utc)
