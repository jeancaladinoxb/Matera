from abc import ABC, abstractmethod


class VincularMateraPort(ABC):
    @abstractmethod
    def vincular(self, token: str, mac: str, codigo: str) -> None:
        """Link the matera to the user identified by the session token.

        The user id comes only from the token, never from the request body.

        Raises:
            InvalidTokenError: if the session token is not valid.
            ValidationError: if the MAC format is invalid.
            MateraOCodigoInvalidoError: if the code is wrong or the matera is unknown.
            MateraYaVinculadaError: if the matera already belongs to a user.
        """
