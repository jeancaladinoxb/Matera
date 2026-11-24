import unittest

from backend.panelPrincipal.domain import (
    IdentificadorPanelInvalidoError,
    MateraPanel,
    PanelPrincipal,
    PanelPrincipalDomainError,
    UsuarioPanel,
    ValorPanelInvalidoError,
)


class UsuarioPanelTests(unittest.TestCase):
    def test_requires_positive_identifier_and_nonempty_names(self) -> None:
        for invalid_id in (0, -1, True):
            with self.subTest(usuario_id=invalid_id):
                with self.assertRaises(IdentificadorPanelInvalidoError):
                    UsuarioPanel(invalid_id, "Ana", "anap")

        for nombre, nickname in (("", "anap"), ("Ana", "  ")):
            with self.subTest(nombre=nombre, nickname=nickname):
                with self.assertRaises(ValorPanelInvalidoError):
                    UsuarioPanel(1, nombre, nickname)


class MateraPanelTests(unittest.TestCase):
    def test_linked_matera_can_have_no_plant_and_device_id_matches_matera(self) -> None:
        matera = MateraPanel(12, "E072A1D55B18")

        self.assertIsNone(matera.planta_id)
        self.assertEqual(matera.dispositivo_id, matera.matera_id)

    def test_rejects_invalid_identifiers_and_mac(self) -> None:
        for invalid_id in (0, -1, True):
            with self.subTest(matera_id=invalid_id):
                with self.assertRaises(IdentificadorPanelInvalidoError):
                    MateraPanel(invalid_id, "E072A1D55B18")

        for mac in ("", "E072A1D55B1", "E072A1D55B1Z", "e072a1d55b18"):
            with self.subTest(mac=mac):
                with self.assertRaises(ValorPanelInvalidoError):
                    MateraPanel(12, mac)

        with self.assertRaises(IdentificadorPanelInvalidoError):
            MateraPanel(12, "E072A1D55B18", planta_id=0)


class PanelPrincipalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.usuario = UsuarioPanel(7, "Ana", "anap")

    def test_contains_multiple_linked_materas(self) -> None:
        panel = PanelPrincipal(
            self.usuario,
            (
                MateraPanel(12, "E072A1D55B18"),
                MateraPanel(13, "246F28AB1234", planta_id=5),
            ),
        )

        self.assertEqual(len(panel.materas), 2)
        self.assertEqual(panel.materas[1].planta_id, 5)

    def test_empty_materas_is_a_valid_panel(self) -> None:
        panel = PanelPrincipal(self.usuario, ())

        self.assertEqual(panel.materas, ())

    def test_materas_are_immutable_and_duplicate_ids_are_rejected(self) -> None:
        materas = [MateraPanel(12, "E072A1D55B18")]
        panel = PanelPrincipal(self.usuario, materas)
        materas.append(MateraPanel(13, "246F28AB1234"))

        self.assertEqual(len(panel.materas), 1)

        with self.assertRaises(PanelPrincipalDomainError):
            PanelPrincipal(
                self.usuario,
                (
                    MateraPanel(12, "E072A1D55B18"),
                    MateraPanel(12, "246F28AB1234"),
                ),
            )


if __name__ == "__main__":
    unittest.main()
