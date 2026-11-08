import unittest
from typing import Optional

from backend.usuarios.application.ports.output import (
    CredencialesUsuario,
    PasswordHasherPort,
    TokenProviderPort,
    UsuarioRepositoryPort,
)
from backend.usuarios.application.use_cases import (
    IniciarSesionUseCase,
    RegistrarUsuarioUseCase,
)
from backend.usuarios.domain import (
    Email,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidPasswordError,
    MissingRequiredFieldError,
    Usuario,
)


class InMemoryUsuarioRepository(UsuarioRepositoryPort):
    def __init__(self) -> None:
        self.users = {}
        self.next_id = 1
        self.saved_users = []

    def existe_por_correo(self, correo: Email) -> bool:
        return correo.value in self.users

    def guardar(self, usuario: Usuario, password_hash: str) -> int:
        usuario_id = self.next_id
        self.next_id += 1
        self.users[usuario.correo.value] = CredencialesUsuario(usuario_id, password_hash)
        self.saved_users.append((usuario, password_hash))
        return usuario_id

    def obtener_credenciales(self, correo: Email) -> Optional[CredencialesUsuario]:
        return self.users.get(correo.value)


class FakePasswordHasher(PasswordHasherPort):
    def __init__(self) -> None:
        self.hashed_passwords = []
        self.verified_passwords = []

    def hashear(self, contrasena) -> str:
        self.hashed_passwords.append(contrasena.value)
        return "hash:{}".format(contrasena.value)

    def verificar(self, contrasena: str, password_hash: str) -> bool:
        self.verified_passwords.append((contrasena, password_hash))
        return password_hash == "hash:{}".format(contrasena)


class FakeTokenProvider(TokenProviderPort):
    def __init__(self) -> None:
        self.user_ids = []

    def generar_token(self, usuario_id: int) -> str:
        self.user_ids.append(usuario_id)
        return "token-for-{}".format(usuario_id)


class RegistrarUsuarioUseCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryUsuarioRepository()
        self.hasher = FakePasswordHasher()
        self.token_provider = FakeTokenProvider()
        self.use_case = RegistrarUsuarioUseCase(
            self.repository, self.hasher, self.token_provider
        )

    def registrar(self, **overrides) -> str:
        values = {
            "nombre": "Ana",
            "apellido": "Pérez",
            "nickname": "anap",
            "correo": " Ana@Example.COM ",
            "contrasena": "Clave123",
        }
        values.update(overrides)
        return self.use_case.registrar(**values)

    def test_registers_user_hashes_password_and_returns_token(self) -> None:
        token = self.registrar()

        self.assertEqual(token, "token-for-1")
        self.assertEqual(self.token_provider.user_ids, [1])
        self.assertEqual(self.hasher.hashed_passwords, ["Clave123"])
        self.assertEqual(len(self.repository.saved_users), 1)
        usuario, password_hash = self.repository.saved_users[0]
        self.assertEqual(usuario.correo.value, "ana@example.com")
        self.assertEqual(password_hash, "hash:Clave123")

    def test_duplicate_email_fails_before_hashing(self) -> None:
        self.registrar()
        self.hasher.hashed_passwords.clear()

        with self.assertRaises(EmailAlreadyRegisteredError):
            self.registrar(correo="ana@example.com")

        self.assertEqual(self.hasher.hashed_passwords, [])
        self.assertEqual(len(self.repository.saved_users), 1)

    def test_validation_errors_prevent_persistence(self) -> None:
        invalid_inputs = (
            ({"correo": "no-es-email"}, InvalidEmailError),
            ({"contrasena": "clave123"}, InvalidPasswordError),
            ({"nombre": " "}, MissingRequiredFieldError),
        )
        for overrides, error_type in invalid_inputs:
            with self.subTest(error=error_type.__name__):
                with self.assertRaises(error_type):
                    self.registrar(**overrides)
        self.assertEqual(self.repository.saved_users, [])


class IniciarSesionUseCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryUsuarioRepository()
        self.hasher = FakePasswordHasher()
        self.token_provider = FakeTokenProvider()
        self.use_case = IniciarSesionUseCase(
            self.repository, self.hasher, self.token_provider
        )

    def test_login_verifies_plaintext_and_issues_token_for_user_id(self) -> None:
        registration = RegistrarUsuarioUseCase(
            self.repository, self.hasher, self.token_provider
        )
        registration.registrar(
            nombre="Ana",
            apellido="Pérez",
            nickname="anap",
            correo="ana@example.com",
            contrasena="Clave123",
        )
        self.hasher.verified_passwords.clear()
        self.token_provider.user_ids.clear()

        token = self.use_case.iniciar_sesion(" ANA@example.com ", "Clave123")

        self.assertEqual(token, "token-for-1")
        self.assertEqual(self.hasher.verified_passwords, [("Clave123", "hash:Clave123")])
        self.assertEqual(self.token_provider.user_ids, [1])

    def test_invalid_email_is_reported_as_invalid_credentials(self) -> None:
        with self.assertRaises(InvalidCredentialsError):
            self.use_case.iniciar_sesion("invalid", "anything")
        self.assertEqual(self.hasher.verified_passwords, [])

    def test_unknown_email_is_reported_as_invalid_credentials(self) -> None:
        with self.assertRaises(InvalidCredentialsError):
            self.use_case.iniciar_sesion("unknown@example.com", "Clave123")
        self.assertEqual(self.hasher.verified_passwords, [])

    def test_wrong_password_is_reported_as_invalid_credentials(self) -> None:
        registration = RegistrarUsuarioUseCase(
            self.repository, self.hasher, self.token_provider
        )
        registration.registrar(
            nombre="Ana",
            apellido="Pérez",
            nickname="anap",
            correo="ana@example.com",
            contrasena="Clave123",
        )
        with self.assertRaises(InvalidCredentialsError):
            self.use_case.iniciar_sesion("ana@example.com", "Incorrecta123")


if __name__ == "__main__":
    unittest.main()
