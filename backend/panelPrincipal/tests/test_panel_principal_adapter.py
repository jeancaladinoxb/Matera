import unittest
from typing import Optional

from flask import Flask

from backend.panelPrincipal.application.ports.input import (
    ConsultarPanelPrincipalPort,
)
from backend.panelPrincipal.application.resultado_consulta_panel import (
    ConsultaPanelExitosa,
    ConsultaPanelFallida,
    ErrorConsultaPanel,
    ResultadoConsultarPanelPrincipal,
)
from backend.panelPrincipal.domain import MateraPanel, PanelPrincipal, UsuarioPanel
from backend.panelPrincipal.infrastructure.controllers import PanelPrincipalAdapter


class FakeConsultarPanel(ConsultarPanelPrincipalPort):
    def __init__(self) -> None:
        self.resultado: ResultadoConsultarPanelPrincipal = ConsultaPanelExitosa(
            PanelPrincipal(UsuarioPanel(7, "Ana", "anap"), ())
        )
        self.usuario_ids = []
        self.error: Optional[Exception] = None

    def consultar(self, usuario_id: int) -> ResultadoConsultarPanelPrincipal:
        self.usuario_ids.append(usuario_id)
        if self.error is not None:
            raise self.error
        return self.resultado


class PanelPrincipalAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.consultar_panel = FakeConsultarPanel()
        self.app = Flask(__name__)
        PanelPrincipalAdapter(
            self.consultar_panel,
            lambda token: 7 if token == "valid-token" else None,
            "cuida_mate_session",
        ).register_routes(self.app)
        self.client = self.app.test_client()

    def test_returns_panel_fields_and_does_not_use_ids_from_request(self) -> None:
        self.consultar_panel.resultado = ConsultaPanelExitosa(
            PanelPrincipal(
                UsuarioPanel(7, "Ana", "anap"),
                (MateraPanel(12, "E072A1D55B18"),),
            )
        )
        self.client.set_cookie("cuida_mate_session", "valid-token")

        response = self.client.get("/panel?usuario_id=99")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "usuario": {
                    "usuario_id": 7,
                    "nombre": "Ana",
                    "nickname": "anap",
                },
                "materas": [
                    {
                        "matera_id": 12,
                        "dispositivo_id": 12,
                        "mac": "E072A1D55B18",
                        "planta_id": None,
                    }
                ],
            },
        )
        self.assertEqual(self.consultar_panel.usuario_ids, [7])
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_missing_or_invalid_session_returns_401_without_querying(self) -> None:
        missing = self.client.get("/panel")
        self.client.set_cookie("cuida_mate_session", "invalid-token")
        invalid = self.client.get("/panel")

        self.assertEqual(missing.status_code, 401)
        self.assertEqual(invalid.status_code, 401)
        self.assertEqual(self.consultar_panel.usuario_ids, [])

    def test_user_not_found_returns_generic_404(self) -> None:
        self.consultar_panel.resultado = ConsultaPanelFallida(
            ErrorConsultaPanel.USUARIO_NO_ENCONTRADO
        )
        self.client.set_cookie("cuida_mate_session", "valid-token")

        response = self.client.get("/panel")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Recurso no encontrado"})

    def test_application_failures_return_generic_500(self) -> None:
        self.client.set_cookie("cuida_mate_session", "valid-token")

        for error in (
            ErrorConsultaPanel.ERROR_ACCESO_DATOS,
            ErrorConsultaPanel.ERROR_DESCONOCIDO,
        ):
            self.consultar_panel.resultado = ConsultaPanelFallida(error)
            response = self.client.get("/panel")

            self.assertEqual(response.status_code, 500)
            self.assertEqual(
                response.get_json(),
                {"error": "Error interno del servidor"},
            )

    def test_unexpected_error_is_generic_500(self) -> None:
        self.consultar_panel.error = RuntimeError("sensitive details")
        self.client.set_cookie("cuida_mate_session", "valid-token")

        response = self.client.get("/panel")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_json(),
            {"error": "Error interno del servidor"},
        )
        self.assertNotIn("sensitive details", response.get_data(as_text=True))
