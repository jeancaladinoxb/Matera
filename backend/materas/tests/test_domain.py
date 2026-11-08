import unittest
from datetime import datetime, timezone

from backend.materas.domain import (
    EstadoMatera,
    InvalidMacError,
    Mac,
    Matera,
    MateraYaVinculadaError,
)


class MacTests(unittest.TestCase):
    def test_normalizes_every_accepted_format(self) -> None:
        for raw in ("24:6F:28:AB:12:34", "246f28ab1234", "24-6f-28-ab-12-34", " 246F28AB1234 "):
            self.assertEqual(Mac(raw).value, "246F28AB1234")

    def test_rejects_invalid_formats(self) -> None:
        for raw in ("", "246F28AB123", "246F28AB12345", "246F28AB123G", "24:6F:28:AB:12", None, 123):
            with self.assertRaises(InvalidMacError):
                Mac(raw)


class MateraTests(unittest.TestCase):
    def test_new_matera_is_unclaimed(self) -> None:
        matera = Matera(Mac("246F28AB1234"))
        self.assertEqual(matera.estado, EstadoMatera.SIN_RECLAMAR)
        self.assertIsNone(matera.usuario_id)
        self.assertIsNone(matera.fecha_vinculacion)
        self.assertFalse(matera.esta_vinculada)

    def test_reclamar_returns_linked_matera(self) -> None:
        fecha = datetime(2026, 1, 1, tzinfo=timezone.utc)
        matera = Matera(Mac("246F28AB1234")).reclamar(7, fecha)
        self.assertTrue(matera.esta_vinculada)
        self.assertEqual(matera.usuario_id, 7)
        self.assertEqual(matera.fecha_vinculacion, fecha)

    def test_linked_matera_cannot_be_claimed_again(self) -> None:
        matera = Matera(Mac("246F28AB1234")).reclamar(7)
        with self.assertRaises(MateraYaVinculadaError):
            matera.reclamar(8)

    def test_incoherent_state_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Matera(Mac("246F28AB1234"), usuario_id=1)
        with self.assertRaises(ValueError):
            Matera(Mac("246F28AB1234"), estado=EstadoMatera.VINCULADA)


if __name__ == "__main__":
    unittest.main()
