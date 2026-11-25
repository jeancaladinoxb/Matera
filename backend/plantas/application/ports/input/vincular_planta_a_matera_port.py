from abc import ABC, abstractmethod


class VincularPlantaAMateraPort(ABC):
    @abstractmethod
    def vincular(self, token: str, matera_id: int, planta_id: int) -> None:
        """Assign the plant to a matera of the user identified by the session.

        Replaces any previous plant; assigning the same plant again is valid.

        Raises:
            InvalidTokenError: if the session token is not valid.
            ValidationError: if an id is not a positive integer.
            PlantaNoEncontradaError: if the plant does not exist.
            MateraNoEncontradaError: if the matera does not exist, is not
                linked, or belongs to another user.
            RepositoryError: if the persistence layer fails.
        """
