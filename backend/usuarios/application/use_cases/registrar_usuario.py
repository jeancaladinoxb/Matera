from backend.usuarios.application.ports.input import RegistrarUsuarioPort
from backend.usuarios.application.ports.output import (
    PasswordHasherPort,
    TokenProviderPort,
    UsuarioRepositoryPort,
)
from backend.usuarios.domain import Email, EmailAlreadyRegisteredError, Password, Usuario


class RegistrarUsuarioUseCase(RegistrarUsuarioPort):
    def __init__(
        self,
        usuario_repository: UsuarioRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_provider: TokenProviderPort,
    ) -> None:
        self._usuario_repository = usuario_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider

    def registrar(
        self,
        *,
        nombre: str,
        apellido: str,
        nickname: str,
        correo: str,
        contrasena: str,
    ) -> str:
        email = Email(correo)
        password = Password(contrasena)
        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            nickname=nickname,
            correo=email,
            contrasena=password,
        )

        if self._usuario_repository.existe_por_correo(email):
            raise EmailAlreadyRegisteredError()

        password_hash = self._password_hasher.hashear(password)
        usuario_id = self._usuario_repository.guardar(usuario, password_hash)
        return self._token_provider.generar_token(usuario_id)
