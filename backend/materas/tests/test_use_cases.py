import unittest
from typing import Optional

from backend.materas.application.ports.output import (
    ClaimCodeVerifierPort,
    DeviceTokenProviderPort,
    MateraRepositoryPort,
)
from backend.materas.application.use_cases import (
    ActivarDispositivoUseCase,
    VincularMateraUseCase,
)
from backend.materas.domain import (
    InvalidMacError,
    Mac,
    Matera,
    MateraNoVinculadaError,
    MateraOCodigoInvalidoError,
    MateraYaVinculadaError,
)
from backend.usuarios.application.ports.output import TokenProviderPort
from backend.usuarios.domain import InvalidTokenError

MAC = "246F28AB1234"
CODIGO = "9f3a1c7e0b52"


class InMemoryMateraRepository(MateraRepositoryPort):
    def __init__(self) -> None:
        self.materas = {}
        self.lookups = 0
        self.lose_race = False

    def buscar_por_mac(self, mac: Mac) -> Optional[Matera]:
        self.lookups += 1
        return self.materas.get(mac.value)

    def registrar(self, matera: Matera) -> bool:
        if matera.mac.value in self.materas:
            return False
        self.materas[matera.mac.value] = matera
        return True

    def reclamar(self, mac: Mac, usuario_id: int) -> bool:
        if self.lose_race:
            return False
        matera = self.materas.get(mac.value)
        if matera is None or matera.esta_vinculada:
            return False
        self.materas[mac.value] = matera.reclamar(usuario_id)
        return True


class FakeVerifier(ClaimCodeVerifierPort):
    def verificar(self, mac: Mac, codigo: str) -> bool:
        return mac.value == MAC and codigo == CODIGO

    def generar(self, mac: Mac) -> str:
        return CODIGO


class FakeUserTokens(TokenProviderPort):
    def generar_token(self, usuario_id: int) -> str:
        return "user-token-{}".format(usuario_id)

    def verificar_token(self, token: str) -> int:
        if not token.startswith("user-token-"):
            raise InvalidTokenError()
        return int(token.rsplit("-", 1)[1])


class FakeDeviceTokens(DeviceTokenProviderPort):
    def __init__(self) -> None:
        self.count = 0

    def generar_token(self, mac: Mac) -> str:
        self.count += 1
        return "device-{}-{}".format(mac.value, self.count)


class VincularMateraUseCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryMateraRepository()
        self.repository.registrar(Matera(Mac(MAC)))
        self.use_case = VincularMateraUseCase(
            self.repository, FakeVerifier(), FakeUserTokens()
        )

    def test_links_matera_to_user_from_token(self) -> None:
        self.use_case.vincular("user-token-7", "24:6f:28:ab:12:34", CODIGO)
        matera = self.repository.materas[MAC]
        self.assertTrue(matera.esta_vinculada)
        self.assertEqual(matera.usuario_id, 7)
        self.assertIsNotNone(matera.fecha_vinculacion)

    def test_invalid_token_is_rejected(self) -> None:
        with self.assertRaises(InvalidTokenError):
            self.use_case.vincular("bad", MAC, CODIGO)
        self.assertFalse(self.repository.materas[MAC].esta_vinculada)

    def test_invalid_mac_format(self) -> None:
        with self.assertRaises(InvalidMacError):
            self.use_case.vincular("user-token-7", "xyz", CODIGO)

    def test_wrong_code_fails_without_querying_database(self) -> None:
        with self.assertRaises(MateraOCodigoInvalidoError):
            self.use_case.vincular("user-token-7", MAC, "000000000000")
        self.assertEqual(self.repository.lookups, 0)

    def test_unknown_matera_gives_same_error_as_wrong_code(self) -> None:
        self.repository.materas.clear()
        with self.assertRaises(MateraOCodigoInvalidoError):
            self.use_case.vincular("user-token-7", MAC, CODIGO)

    def test_already_linked_matera_conflicts_and_keeps_owner(self) -> None:
        self.use_case.vincular("user-token-7", MAC, CODIGO)
        with self.assertRaises(MateraYaVinculadaError):
            self.use_case.vincular("user-token-8", MAC, CODIGO)
        self.assertEqual(self.repository.materas[MAC].usuario_id, 7)

    def test_losing_the_atomic_claim_race_conflicts(self) -> None:
        self.repository.lose_race = True
        with self.assertRaises(MateraYaVinculadaError):
            self.use_case.vincular("user-token-7", MAC, CODIGO)


class ActivarDispositivoUseCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryMateraRepository()
        self.repository.registrar(Matera(Mac(MAC)))
        self.use_case = ActivarDispositivoUseCase(
            self.repository, FakeVerifier(), FakeDeviceTokens()
        )

    def test_unlinked_matera_gets_no_token(self) -> None:
        with self.assertRaises(MateraNoVinculadaError):
            self.use_case.activar(MAC, CODIGO)

    def test_linked_matera_gets_token_and_repeat_gets_a_new_one(self) -> None:
        self.repository.reclamar(Mac(MAC), 7)
        first = self.use_case.activar("24:6F:28:AB:12:34", CODIGO)
        second = self.use_case.activar(MAC, CODIGO)
        self.assertTrue(first.startswith("device-" + MAC))
        self.assertNotEqual(first, second)

    def test_wrong_code_and_unknown_matera_share_the_same_error(self) -> None:
        with self.assertRaises(MateraOCodigoInvalidoError):
            self.use_case.activar(MAC, "000000000000")
        self.assertEqual(self.repository.lookups, 0)
        self.repository.materas.clear()
        with self.assertRaises(MateraOCodigoInvalidoError):
            self.use_case.activar(MAC, CODIGO)

    def test_invalid_mac_format(self) -> None:
        with self.assertRaises(InvalidMacError):
            self.use_case.activar("nope", CODIGO)


if __name__ == "__main__":
    unittest.main()
