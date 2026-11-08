import io
import unittest

from backend.materas.cli import registrar_materas
from backend.materas.domain import Mac
from backend.materas.infrastructure.adapters import HmacClaimVerifier
from backend.materas.tests.test_use_cases import InMemoryMateraRepository


class RegistrarMaterasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryMateraRepository()
        self.verifier = HmacClaimVerifier("test-master-key-that-is-long-enough-1234")

    def run_cli(self, macs):
        out, err = io.StringIO(), io.StringIO()
        code = registrar_materas(macs, self.repository, self.verifier, out, err)
        return code, out.getvalue(), err.getvalue()

    def test_registers_and_prints_qr_payload(self) -> None:
        code, out, _ = self.run_cli(["24:6f:28:ab:12:34"])
        codigo = self.verifier.generar(Mac("246F28AB1234"))
        self.assertEqual(code, 0)
        self.assertEqual(out, "MAT:246F28AB1234:{}\n".format(codigo))
        self.assertFalse(self.repository.materas["246F28AB1234"].esta_vinculada)

    def test_is_idempotent_and_never_overwrites(self) -> None:
        self.run_cli(["246F28AB1234"])
        self.repository.reclamar(Mac("246F28AB1234"), 7)
        code, out, err = self.run_cli(["246f28ab1234"])
        self.assertEqual(code, 0)
        self.assertIn("ya existía", err)
        self.assertTrue(out.startswith("MAT:246F28AB1234:"))
        self.assertEqual(self.repository.materas["246F28AB1234"].usuario_id, 7)

    def test_invalid_mac_is_skipped_and_exit_code_is_1(self) -> None:
        code, out, err = self.run_cli(["nope", "246F28AB1234"])
        self.assertEqual(code, 1)
        self.assertEqual(len(out.splitlines()), 1)
        self.assertIn("MAC inválida", err)
        self.assertNotIn(self.verifier.generar(Mac("246F28AB1234")), err)


if __name__ == "__main__":
    unittest.main()
