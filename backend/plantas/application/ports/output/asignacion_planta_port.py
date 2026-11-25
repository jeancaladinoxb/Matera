from abc import ABC, abstractmethod


class AsignacionPlantaPort(ABC):
    @abstractmethod
    def asignar(self, usuario_id: int, matera_id: int, planta_id: int) -> bool:
        """Atomically set the plant of a linked matera that belongs to the user.

        Returns True if a matera was updated (including when it already had this
        plant), False if no linked matera with that id belongs to the user.

        Raises:
            RepositoryError: if the persistence layer fails.
        """
