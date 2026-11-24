import unittest
from typing import Optional, Tuple

from backend.panelPrincipal.application.errors import ErrorAccesoDatosPanelError
from backend.panelPrincipal.application.ports.output import (
    MateraRepositoryPort,
    UsuarioRepositoryPort,
)
from backend.panelPrincipal.application.resultado_consulta_panel import (
    ConsultaPanelExitosa,
    ConsultaPanelFallida,
    ErrorConsultaPanel,
)
from backend.panelPrincipal.application.use_cases import (
    ConsultarPanelPrincipalCasoDeUso,
)
from backend.panelPrincipal.domain import MateraPanel, UsuarioPanel


class FakeUsuarioRepository(UsuarioRepositoryPort):
    def __init__(self) -> None:
        self.usuario: Optional[UsuarioPanel] = UsuarioPanel(7, "Ana", "anap")
        self.error: Optional[Exception] = None
        self.consultas = []

    def consultar_por_id(self, usuario_id: int) -> Optional[UsuarioPanel]:
        self.consultas.append(usuario_id)
        if self.error is not None:
            raise self.error
        return self.usuario


class FakeMateraRepository(MateraRepositoryPort):
    def __init__(self) -> None:
        self.materas: Tuple[MateraPanel, ...] = ()
        self.error: Optional[Exception] = None
        self.consultas = []

    def listar_vinculadas_por_usuario(
        self, usuario_id: int
    ) -> Tuple[MateraPanel, ...]:
        self.consultas.append(usuario_id)
        if self.error is not None:
            raise self.error
        return self.materas


class ConsultarPanelPrincipalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.usuarios = FakeUsuarioRepository()
        self.materas = FakeMateraRepository()
        self.caso_de_uso = ConsultarPanelPrincipalCasoDeUso(
            self.usuarios, self.materas
        )

    def test_returns_panel_with_multiple_materas(self) -> None:
        self.materas.materas = (
            MateraPanel(12, "E072A1D55B18"),
            MateraPanel(13, "246F28AB1234", planta_id=5),
        )

        resultado = self.caso_de_uso.consultar(7)

        self.assertIsInstance(resultado, ConsultaPanelExitosa)
        self.assertEqual(resultado.panel.usuario.usuario_id, 7)
        self.assertEqual(len(resultado.panel.materas), 2)
        self.assertEqual(self.materas.consultas, [7])

    def test_user_without_materas_has_a_valid_empty_panel(self) -> None:
        resultado = self.caso_de_uso.consultar(7)

        self.assertIsInstance(resultado, ConsultaPanelExitosa)
        self.assertEqual(resultado.panel.materas, ())

    def test_missing_user_does_not_query_materas(self) -> None:
        self.usuarios.usuario = None

        resultado = self.caso_de_uso.consultar(99)

        self.assertEqual(
            resultado,
            ConsultaPanelFallida(ErrorConsultaPanel.USUARIO_NO_ENCONTRADO),
        )
        self.assertEqual(self.materas.consultas, [])

    def test_data_access_errors_are_typed(self) -> None:
        self.usuarios.error = ErrorAccesoDatosPanelError()
        resultado_usuario = self.caso_de_uso.consultar(7)
        self.assertEqual(
            resultado_usuario,
            ConsultaPanelFallida(ErrorConsultaPanel.ERROR_ACCESO_DATOS),
        )

        self.usuarios.error = None
        self.materas.error = ErrorAccesoDatosPanelError()
        resultado_matera = self.caso_de_uso.consultar(7)
        self.assertEqual(
            resultado_matera,
            ConsultaPanelFallida(ErrorConsultaPanel.ERROR_ACCESO_DATOS),
        )

    def test_unexpected_error_is_typed_without_exposing_details(self) -> None:
        self.materas.error = RuntimeError("sensitive database detail")

        resultado = self.caso_de_uso.consultar(7)

        self.assertEqual(
            resultado,
            ConsultaPanelFallida(ErrorConsultaPanel.ERROR_DESCONOCIDO),
        )
        self.assertNotIn("sensitive database detail", str(resultado))


if __name__ == "__main__":
    unittest.main()
