from backend.usuarios.application.ports.input import IniciarSesionPort
from backend.usuarios.application.ports.output import (
    PasswordHasherPort,
    TokenProviderPort,
    UsuarioRepositoryPort,
)
from backend.usuarios.domain import Email, InvalidCredentialsError, InvalidEmailError


class IniciarSesionUseCase(IniciarSesionPort):
    def __init__(
        self,
        usuario_repository: UsuarioRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_provider: TokenProviderPort,
    ) -> None:
        self._usuario_repository = usuario_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider

    def iniciar_sesion(self, correo: str, contrasena: str) -> str:
        try:
            email = Email(correo)
        except InvalidEmailError:
            raise InvalidCredentialsError() from None

        credenciales = self._usuario_repository.obtener_credenciales(email)
        if credenciales is None or not self._password_hasher.verificar(
            contrasena, credenciales.password_hash
        ):
            raise InvalidCredentialsError()

        return self._token_provider.generar_token(credenciales.usuario_id)
