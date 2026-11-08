import unittest

from backend.usuarios.domain import Password
from backend.usuarios.infrastructure.adapters import Argon2Hasher


class Argon2HasherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.hasher = Argon2Hasher()

    def test_hashes_same_password_differently_and_verifies_both(self) -> None:
        password = Password("Clave123")

        first_hash = self.hasher.hashear(password)
        second_hash = self.hasher.hashear(password)

        self.assertNotEqual(first_hash, second_hash)
        self.assertTrue(self.hasher.verificar(password.value, first_hash))
        self.assertTrue(self.hasher.verificar(password.value, second_hash))

    def test_wrong_password_returns_false(self) -> None:
        password_hash = self.hasher.hashear(Password("Clave123"))

        self.assertFalse(self.hasher.verificar("Incorrecta123", password_hash))

    def test_invalid_hash_returns_false(self) -> None:
        self.assertFalse(self.hasher.verificar("Clave123", "not-a-valid-hash"))


if __name__ == "__main__":
    unittest.main()
